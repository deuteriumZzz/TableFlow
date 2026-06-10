# Real-time WebSockets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 15-second polling in KitchenPage with Django Channels WebSockets, so the kitchen screen updates instantly when order status changes.

**Architecture:** Django Channels runs as an ASGI app alongside the WSGI app. An `OrderConsumer` (AsyncWebsocketConsumer) subscribes to a per-restaurant channel group; `OrderViewSet.update_status` sends a message to that group on every status change. The frontend uses a custom `useOrderUpdates` hook that opens a WebSocket and merges incoming events into the existing order list from the REST API. Redis is the channel layer backend (required for multi-replica deployments).

**Tech Stack:** channels 4.1, daphne 4.1 (ASGI server), channels-redis 4.2, Redis 7, frontend: native WebSocket API

**Prerequisite:** Plan 01 (Code Cleanup + `api` App) must be merged first.

---

## File Map

**Create:**
- `backend/apps/orders/consumers.py`
- `backend/apps/orders/routing.py`
- `backend/frontend/src/hooks/useOrderUpdates.ts`

**Modify:**
- `backend/requirements.txt` — add channels, daphne, channels-redis
- `backend/config/settings.py` — CHANNEL_LAYERS, ASGI_APPLICATION
- `backend/config/asgi.py` — add WebSocket routing
- `backend/apps/orders/views.py` — send WS message on update_status
- `docker-compose.yml` — add Redis service, change backend to use daphne
- `backend/entrypoint.sh` — switch from gunicorn to daphne
- `frontend/src/pages/KitchenPage.tsx` — use WebSocket hook instead of setInterval
- `k8s/backend/deployment.yaml` — update port/command for daphne

**Create (K8s):**
- `k8s/redis/deployment.yaml`
- `k8s/redis/service.yaml`

---

### Task 1: Add Django Channels dependencies

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/config/settings.py`

- [ ] **Step 1: Add to `backend/requirements.txt`**

Remove `gunicorn` (replaced by daphne) and add:
```
daphne==4.1.2
channels==4.1.0
channels-redis==4.2.1
```

Keep `gunicorn` for now — daphne replaces it in `entrypoint.sh`, not in requirements.

Actually, keep both:
```
gunicorn==21.2.0
daphne==4.1.2
channels==4.1.0
channels-redis==4.2.1
```

- [ ] **Step 2: Update `backend/config/settings.py`**

Add `'daphne'` as the FIRST app in `INSTALLED_APPS` (required for daphne's static file handling):
```python
INSTALLED_APPS = [
    'daphne',              # MUST be first
    'django_prometheus',
    'django.contrib.admin',
    ...
]
```

Add `ASGI_APPLICATION` and `CHANNEL_LAYERS`:
```python
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [config('REDIS_URL', default='redis://localhost:6379/0')],
        },
    },
}
```

- [ ] **Step 3: Install and verify**

```bash
cd backend
pip install daphne==4.1.2 channels==4.1.0 channels-redis==4.2.1
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 4: Commit**

```bash
git add backend/requirements.txt backend/config/settings.py
git commit -m "feat: add Django Channels + daphne + channels-redis dependencies"
```

---

### Task 2: Create ASGI application with WebSocket routing

**Files:**
- Modify: `backend/config/asgi.py`
- Create: `backend/apps/orders/routing.py`

- [ ] **Step 1: Read existing `backend/config/asgi.py`**

```
backend/config/asgi.py
```

It likely contains:
```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_asgi_application()
```

- [ ] **Step 2: Create `backend/apps/orders/routing.py`**

```python
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/orders/$', consumers.OrderConsumer.as_asgi()),
]
```

- [ ] **Step 3: Replace `backend/config/asgi.py`**

```python
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from apps.orders.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
```

- [ ] **Step 4: Commit**

```bash
git add backend/config/asgi.py backend/apps/orders/routing.py
git commit -m "feat: configure ASGI application with WebSocket routing"
```

---

### Task 3: Create `OrderConsumer`

**Files:**
- Create: `backend/apps/orders/consumers.py`

- [ ] **Step 1: Create `backend/apps/orders/consumers.py`**

The consumer joins a per-restaurant channel group. When an order status changes, a message is sent to the group and all connected kitchen screens receive it.

```python
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Order
from .serializers import OrderSerializer


class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return

        self.restaurant_id = user.restaurant_id
        self.group_name = f'orders_restaurant_{self.restaurant_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Clients send {"type": "fetch_orders"} to get current order list
        data = json.loads(text_data)
        if data.get('type') == 'fetch_orders':
            orders = await self._get_active_orders()
            await self.send(text_data=json.dumps({
                'type': 'order_list',
                'orders': orders,
            }))

    async def order_update(self, event):
        """Called when a message is pushed to the group (from views.py)."""
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'order': event['order'],
        }))

    @database_sync_to_async
    def _get_active_orders(self):
        orders = (
            Order.objects
            .filter(
                restaurant_id=self.restaurant_id,
                status__in=('created', 'in_progress', 'ready'),
            )
            .prefetch_related('items__product', 'items__modifiers')
        )
        return OrderSerializer(orders, many=True).data
```

- [ ] **Step 2: Commit**

```bash
git add backend/apps/orders/consumers.py
git commit -m "feat: add OrderConsumer WebSocket consumer"
```

---

### Task 4: Push WebSocket events from `update_status` view

**Files:**
- Modify: `backend/apps/orders/views.py`

- [ ] **Step 1: Read the current `update_status` action in `backend/apps/orders/views.py`**

The current implementation:
```python
@action(detail=True, methods=['post'])
def update_status(self, request, pk=None):
    order = self.get_object()
    new_status = request.data.get('status')
    ...
    order.status = new_status
    ...
    order.save()
    return Response(OrderSerializer(order).data)
```

- [ ] **Step 2: Add channel layer push after status save**

Add these imports at the top of `orders/views.py`:
```python
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
```

Replace the `update_status` action with:
```python
@action(detail=True, methods=['post'])
def update_status(self, request, pk=None):
    order = self.get_object()
    new_status = request.data.get('status')
    valid = [s[0] for s in Order.STATUS_CHOICES]
    if new_status not in valid:
        return Response(
            {'error': f'Допустимые статусы: {valid}'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    order.status = new_status
    if new_status in ('delivered', 'cancelled') and order.table:
        if not Order.objects.filter(
            table=order.table, status__in=('created', 'in_progress', 'ready')
        ).exclude(id=order.id).exists():
            order.table.status = 'free'
            order.table.save()
    order.save()

    # Push real-time update to all kitchen screens for this restaurant
    serialized = OrderSerializer(order).data
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'orders_restaurant_{order.restaurant_id}',
        {
            'type': 'order_update',
            'order': serialized,
        },
    )

    return Response(serialized)
```

- [ ] **Step 3: Commit**

```bash
git add backend/apps/orders/views.py
git commit -m "feat: push WebSocket order_update event on status change"
```

---

### Task 5: Add Redis to docker-compose and K8s

**Files:**
- Modify: `docker-compose.yml`
- Create: `k8s/redis/deployment.yaml`
- Create: `k8s/redis/service.yaml`

- [ ] **Step 1: Add Redis to `docker-compose.yml`**

```yaml
services:
  ...

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    ...
    environment:
      ...
      REDIS_URL: redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
```

- [ ] **Step 2: Create `k8s/redis/deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: tableflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          ports:
            - containerPort: 6379
          command: ["redis-server", "--appendonly", "yes"]
          volumeMounts:
            - name: redis-data
              mountPath: /data
          readinessProbe:
            exec:
              command: ["redis-cli", "ping"]
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              memory: "64Mi"
              cpu: "50m"
            limits:
              memory: "256Mi"
              cpu: "200m"
      volumes:
        - name: redis-data
          emptyDir: {}
```

- [ ] **Step 3: Create `k8s/redis/service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: tableflow
spec:
  selector:
    app: redis
  ports:
    - port: 6379
      targetPort: 6379
```

- [ ] **Step 4: Add `REDIS_URL` to `k8s/backend/configmap.yaml`**

```yaml
data:
  ...
  REDIS_URL: "redis://redis:6379/0"
```

- [ ] **Step 5: Switch backend from gunicorn to daphne in `backend/entrypoint.sh`**

Replace:
```bash
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

With:
```bash
exec daphne config.asgi:application --bind 0.0.0.0 --port 8000 -v 1
```

- [ ] **Step 6: Test with docker-compose**

```bash
docker compose up --build -d
sleep 10
curl -s http://localhost:8000/api/health/
```

Expected: `{"status":"ok","db":true}`

Test WebSocket connection (requires `wscat`):
```bash
npm install -g wscat
# Get a JWT token first:
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")
# Connect to WebSocket:
wscat -c "ws://localhost:8000/ws/orders/?token=$TOKEN"
```

Expected: WebSocket connects and responds to `{"type":"fetch_orders"}`.

- [ ] **Step 7: Commit**

```bash
git add docker-compose.yml backend/entrypoint.sh k8s/redis/ k8s/backend/configmap.yaml
git commit -m "feat: add Redis to docker-compose and K8s; switch backend to daphne ASGI server"
```

---

### Task 6: Frontend — `useOrderUpdates` WebSocket hook

**Files:**
- Create: `frontend/src/hooks/useOrderUpdates.ts`

- [ ] **Step 1: Create `frontend/src/hooks/useOrderUpdates.ts`**

The hook opens a WebSocket, sends `fetch_orders` on connect, and calls `onUpdate` whenever an `order_update` event arrives. It handles reconnection with exponential backoff.

```typescript
import { useEffect, useRef, useCallback } from 'react'
import type { Order } from '../types'

interface OrderUpdateEvent {
  type: 'order_update'
  order: Order
}

interface OrderListEvent {
  type: 'order_list'
  orders: Order[]
}

type WsEvent = OrderUpdateEvent | OrderListEvent

interface Options {
  onOrderList: (orders: Order[]) => void
  onOrderUpdate: (order: Order) => void
}

const WS_BASE = import.meta.env.VITE_WS_URL ?? `ws://${window.location.host}`

export function useOrderUpdates({ onOrderList, onOrderUpdate }: Options) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const attemptsRef = useRef(0)

  const connect = useCallback(() => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const ws = new WebSocket(`${WS_BASE}/ws/orders/?token=${token}`)
    wsRef.current = ws

    ws.onopen = () => {
      attemptsRef.current = 0
      ws.send(JSON.stringify({ type: 'fetch_orders' }))
    }

    ws.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as WsEvent
        if (data.type === 'order_list') {
          onOrderList(data.orders)
        } else if (data.type === 'order_update') {
          onOrderUpdate(data.order)
        }
      } catch {
        // malformed message — ignore
      }
    }

    ws.onclose = () => {
      const delay = Math.min(1000 * 2 ** attemptsRef.current, 30000)
      attemptsRef.current += 1
      reconnectTimeoutRef.current = setTimeout(connect, delay)
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [onOrderList, onOrderUpdate])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current)
      wsRef.current?.close()
    }
  }, [connect])
}
```

- [ ] **Step 2: Add `VITE_WS_URL` to `frontend/.env.example`**

Create `frontend/.env.example`:
```
VITE_WS_URL=ws://localhost:8000
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/hooks/useOrderUpdates.ts frontend/.env.example
git commit -m "feat: add useOrderUpdates WebSocket hook with exponential backoff reconnect"
```

---

### Task 7: Update `KitchenPage.tsx` — replace polling with WebSocket

**Files:**
- Modify: `frontend/src/pages/KitchenPage.tsx`

- [ ] **Step 1: Read the current `frontend/src/pages/KitchenPage.tsx`**

```
frontend/src/pages/KitchenPage.tsx
```

The current implementation uses `setInterval(() => loadOrders(), 15000)`.

- [ ] **Step 2: Replace with WebSocket-driven updates**

```typescript
import { useState, useCallback, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'
import { useOrderUpdates } from '../hooks/useOrderUpdates'
import StatusBadge from '../components/StatusBadge'
import type { Order } from '../types'
import client from '../api/client'

const ACTIVE_STATUSES = ['created', 'in_progress', 'ready'] as const
type ActiveStatus = typeof ACTIVE_STATUSES[number]

const STATUS_LABELS: Record<ActiveStatus, string> = {
  created: 'Новые',
  in_progress: 'Готовится',
  ready: 'Готово',
}

const NEXT_STATUS: Record<ActiveStatus, string> = {
  created: 'in_progress',
  in_progress: 'ready',
  ready: 'delivered',
}

export default function KitchenPage() {
  const user = useAuthStore((s) => s.user)
  const [orders, setOrders] = useState<Order[]>([])
  const [advancing, setAdvancing] = useState<number | null>(null)

  const handleOrderList = useCallback((list: Order[]) => {
    setOrders(list)
  }, [])

  const handleOrderUpdate = useCallback((updated: Order) => {
    setOrders((prev) => {
      const idx = prev.findIndex((o) => o.id === updated.id)
      if (!ACTIVE_STATUSES.includes(updated.status as ActiveStatus)) {
        // Order left the kitchen board — remove it
        return prev.filter((o) => o.id !== updated.id)
      }
      if (idx === -1) return [...prev, updated]
      const next = [...prev]
      next[idx] = updated
      return next
    })
  }, [])

  useOrderUpdates({ onOrderList: handleOrderList, onOrderUpdate: handleOrderUpdate })

  const advance = async (order: Order) => {
    if (!(order.status in NEXT_STATUS)) return
    setAdvancing(order.id)
    try {
      await client.post(`/orders/${order.id}/update_status/`, {
        status: NEXT_STATUS[order.status as ActiveStatus],
      })
      // The WebSocket will deliver the update — no need to patch state here
    } finally {
      setAdvancing(null)
    }
  }

  const columns = ACTIVE_STATUSES.map((s) => ({
    status: s,
    label: STATUS_LABELS[s],
    orders: orders.filter((o) => o.status === s),
  }))

  if (!user) return null

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Кухня</h1>
        <span className="text-sm text-green-600 font-medium">● Live</span>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {columns.map(({ status, label, orders: col }) => (
          <div key={status} className="bg-white rounded-xl shadow p-4">
            <h2 className="font-semibold text-gray-700 mb-3">
              {label} <span className="text-gray-400 font-normal">({col.length})</span>
            </h2>
            <div className="space-y-3">
              {col.map((order) => (
                <div key={order.id} className="border border-gray-200 rounded-lg p-3">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-gray-800">
                      #{order.id} · Стол {order.table_number ?? '—'}
                    </span>
                    <StatusBadge status={order.status} />
                  </div>
                  <ul className="text-sm text-gray-600 mb-3 space-y-0.5">
                    {order.items.map((item) => (
                      <li key={item.id}>
                        {item.quantity}× {item.product?.name ?? '—'}
                      </li>
                    ))}
                  </ul>
                  {status !== 'ready' || order.status === 'ready' ? (
                    <button
                      onClick={() => advance(order)}
                      disabled={advancing === order.id}
                      className="w-full text-sm bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-1.5 rounded-lg transition-colors"
                    >
                      {advancing === order.id
                        ? 'Обновление...'
                        : status === 'created'
                        ? 'В работу'
                        : status === 'in_progress'
                        ? 'Готово'
                        : 'Выдать'}
                    </button>
                  ) : null}
                </div>
              ))}
              {col.length === 0 && (
                <p className="text-gray-400 text-sm text-center py-4">Пусто</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Add `VITE_WS_URL` to `frontend/nginx.conf` proxy for production**

In `frontend/nginx.conf`, add WebSocket proxy alongside the existing `/api` proxy:

```nginx
location /ws/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 86400;
}
```

- [ ] **Step 4: Build and test**

```bash
cd frontend
npm run build
```

Expected: build succeeds with no TypeScript errors.

- [ ] **Step 5: Integration test (manual)**

```bash
docker compose up --build -d
sleep 10
```

1. Open `http://localhost/kitchen` in browser — kitchen page loads, `● Live` indicator visible
2. Open `http://localhost` in another tab — log in as waiter, create an order
3. Observe: the new order appears on the kitchen page in the "Новые" column **without page refresh**
4. Click "В работу" — order moves to "Готовится" **instantly**

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/KitchenPage.tsx frontend/nginx.conf
git commit -m "feat: replace polling with WebSocket in KitchenPage; add nginx WS proxy"
```

---

### Task 8: Handle WebSocket JWT auth in Django Channels

The `AuthMiddlewareStack` from channels does not natively support JWT tokens passed as query parameters. We need a custom middleware.

**Files:**
- Create: `backend/apps/api/middleware.py`
- Modify: `backend/config/asgi.py`

- [ ] **Step 1: Create `backend/apps/api/middleware.py`**

```python
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken


@database_sync_to_async
def get_user_from_token(token_key):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        token = AccessToken(token_key)
        return User.objects.get(id=token['user_id'])
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """Authenticate WebSocket connections using a JWT token in the query string."""

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token_list = params.get('token', [None])
        token_key = token_list[0]

        if token_key:
            scope['user'] = await get_user_from_token(token_key)
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
```

- [ ] **Step 2: Update `backend/config/asgi.py` to use `JWTAuthMiddleware`**

```python
import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from apps.api.middleware import JWTAuthMiddleware
from apps.orders.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
```

- [ ] **Step 3: Add `ALLOWED_HOSTS` entry for WebSocket in dev**

In `backend/config/settings.py`, update `ALLOWED_HOSTS`:
```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')
```

And for WebSocket origin validation, add:
```python
# Allow all origins in dev; restrict in production via ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://localhost').split(',')
```

- [ ] **Step 4: Commit**

```bash
git add backend/apps/api/middleware.py backend/config/asgi.py backend/config/settings.py
git commit -m "feat: add JWT WebSocket auth middleware; replace AuthMiddlewareStack"
```

---

### Task 9: K8s — update backend deployment for ASGI

**Files:**
- Modify: `k8s/backend/deployment.yaml`

- [ ] **Step 1: The current liveness probe path is already `/api/health/` from Plan 01**

No change needed there.

- [ ] **Step 2: Ensure the K8s backend service exposes the correct port (already port 8000)**

Verify `k8s/backend/service.yaml` already has port 8000. If it already has `name: http` on port 8000 from Plan 03, no change needed.

- [ ] **Step 3: Add Redis to K8s backend configmap**

In `k8s/backend/configmap.yaml`, ensure this line exists (added in Task 5):
```yaml
  REDIS_URL: "redis://redis:6379/0"
```

- [ ] **Step 4: Apply all new k8s resources**

```bash
kubectl apply -f k8s/redis/
kubectl apply -f k8s/backend/configmap.yaml
kubectl rollout restart deployment/backend -n tableflow
kubectl rollout status deployment/backend -n tableflow
```

Expected: `deployment "backend" successfully rolled out`

- [ ] **Step 5: Final commit**

```bash
git add k8s/
git commit -m "chore: apply Redis + ASGI changes to K8s deployment"
```
