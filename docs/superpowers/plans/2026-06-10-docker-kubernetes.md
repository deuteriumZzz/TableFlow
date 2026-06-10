# Docker + Kubernetes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the TableFlow POS system for containerized deployment using Docker Compose (local) and Kubernetes (production).

**Architecture:** Backend runs in a Python/gunicorn container; frontend is built by Node and served by nginx. PostgreSQL replaces SQLite in containerized environments. Docker Compose wires everything together for local development; Kubernetes manifests (in `k8s/`) provide production-grade deployment with Deployments, Services, Secrets, and Ingress.

**Tech Stack:** Docker, Docker Compose v2, gunicorn 21, psycopg2-binary, dj-database-url, nginx:alpine, Kubernetes 1.28+

---

## File Map

```
backend/requirements.txt              MODIFY  — add gunicorn, psycopg2-binary, dj-database-url
backend/config/settings.py            MODIFY  — read DB/secret/debug from env vars
backend/Dockerfile                    CREATE
backend/.dockerignore                 CREATE
backend/entrypoint.sh                 CREATE  — migrate + collectstatic + exec gunicorn

frontend/Dockerfile                   CREATE  — 2-stage: node build → nginx serve
frontend/.dockerignore                CREATE
frontend/nginx.conf                   CREATE  — SPA routing + /api proxy

docker-compose.yml                    CREATE  — postgres + backend + frontend
.env.example                          CREATE  — template for .env file

k8s/
  namespace.yaml                      CREATE
  postgres/
    secret.yaml                       CREATE  — DB credentials
    pvc.yaml                          CREATE  — 5Gi persistent volume
    deployment.yaml                   CREATE
    service.yaml                      CREATE  — ClusterIP on 5432
  backend/
    secret.yaml                       CREATE  — SECRET_KEY + DATABASE_URL
    configmap.yaml                    CREATE  — DEBUG=False, ALLOWED_HOSTS, etc.
    deployment.yaml                   CREATE  — 2 replicas, liveness/readiness probes
    service.yaml                      CREATE  — ClusterIP on 8000
  frontend/
    deployment.yaml                   CREATE  — 2 replicas
    service.yaml                      CREATE  — ClusterIP on 80
  ingress.yaml                        CREATE  — /api → backend, / → frontend
```

---

## Task 1: Update backend for production readiness

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/config/settings.py`

- [ ] **Step 1: Add production packages to requirements.txt**

```
# backend/requirements.txt
Django==4.2.30
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
Pillow==10.4.0
sqlparse==0.5.5
asgiref==3.11.1
gunicorn==21.2.0
psycopg2-binary==2.9.9
dj-database-url==2.2.0
python-decouple==3.8
```

- [ ] **Step 2: Update settings.py to read from environment**

Replace `backend/config/settings.py` with:

```python
from pathlib import Path
from datetime import timedelta
import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-!b5&*m=!m_wl_cf936cs@v6r#1m7(pgws!w*5)*4iy&mc4m5av')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'apps.accounts',
    'apps.restaurants',
    'apps.tables',
    'apps.menu',
    'apps.orders',
    'apps.payments',
    'apps.staff',
    'apps.reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = config(
    'DATABASE_URL',
    default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'
)
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',') if not CORS_ALLOW_ALL_ORIGINS else []
```

- [ ] **Step 3: Install new packages in venv (for local dev)**

```bash
cd /Users/deuterium/Dev/TableFlow && source venv/bin/activate && pip install gunicorn==21.2.0 psycopg2-binary==2.9.9 dj-database-url==2.2.0 python-decouple==3.8
```

Expected: packages install without errors.

- [ ] **Step 4: Verify Django check still passes**

```bash
cd /Users/deuterium/Dev/TableFlow && source venv/bin/activate && cd backend && python manage.py check 2>&1
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 5: Commit**

```bash
cd /Users/deuterium/Dev/TableFlow && git add backend/requirements.txt backend/config/settings.py && git commit -m "feat: add gunicorn/postgres support, read config from env vars"
```

---

## Task 2: Backend Dockerfile + entrypoint

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`
- Create: `backend/entrypoint.sh`

- [ ] **Step 1: Create backend/entrypoint.sh**

```bash
#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

Make it executable:
```bash
chmod +x /Users/deuterium/Dev/TableFlow/backend/entrypoint.sh
```

- [ ] **Step 2: Create backend/Dockerfile**

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
```

- [ ] **Step 3: Create backend/.dockerignore**

```
__pycache__/
*.pyc
*.pyo
.Python
*.egg-info/
.git/
.gitignore
db.sqlite3
media/
staticfiles/
.env
*.log
venv/
```

- [ ] **Step 4: Verify build**

```bash
cd /Users/deuterium/Dev/TableFlow/backend && docker build -t tableflow-backend:test . 2>&1 | tail -10
```

Expected: `Successfully built ...` (or `=> exporting to image` for BuildKit).

- [ ] **Step 5: Commit**

```bash
cd /Users/deuterium/Dev/TableFlow && git add backend/Dockerfile backend/.dockerignore backend/entrypoint.sh && git commit -m "feat: add backend Dockerfile with gunicorn entrypoint"
```

---

## Task 3: Frontend Dockerfile + nginx config

**Files:**
- Create: `frontend/Dockerfile`
- Create: `frontend/.dockerignore`
- Create: `frontend/nginx.conf`

- [ ] **Step 1: Create frontend/nginx.conf**

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Serve static assets with caching
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy media files
    location /media/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }

    # React SPA — all other routes serve index.html
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

- [ ] **Step 2: Create frontend/Dockerfile**

```dockerfile
# Stage 1: build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **Step 3: Create frontend/.dockerignore**

```
node_modules/
dist/
.git/
.gitignore
*.md
.env*
```

- [ ] **Step 4: Verify frontend build (Docker)**

```bash
cd /Users/deuterium/Dev/TableFlow/frontend && docker build -t tableflow-frontend:test . 2>&1 | tail -10
```

Expected: `Successfully built ...`

- [ ] **Step 5: Commit**

```bash
cd /Users/deuterium/Dev/TableFlow && git add frontend/Dockerfile frontend/.dockerignore frontend/nginx.conf && git commit -m "feat: add frontend Dockerfile (Node build + nginx serve)"
```

---

## Task 4: Docker Compose + .env template

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Update: `.gitignore` (ensure `.env` is excluded)

- [ ] **Step 1: Create .env.example**

```
# Copy this file to .env and fill in the values
# cp .env.example .env

# Django
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOW_ALL_ORIGINS=True

# Database (used by Django and postgres service)
POSTGRES_DB=tableflow
POSTGRES_USER=tableflow
POSTGRES_PASSWORD=tableflow_dev_password
DATABASE_URL=postgresql://tableflow:tableflow_dev_password@postgres:5432/tableflow
```

- [ ] **Step 2: Create docker-compose.yml**

```yaml
services:
  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-tableflow}
      POSTGRES_USER: ${POSTGRES_USER:-tableflow}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-tableflow_dev_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-tableflow}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      SECRET_KEY: ${SECRET_KEY:-django-insecure-change-me}
      DEBUG: ${DEBUG:-True}
      ALLOWED_HOSTS: ${ALLOWED_HOSTS:-localhost,127.0.0.1,backend}
      DATABASE_URL: ${DATABASE_URL:-postgresql://tableflow:tableflow_dev_password@postgres:5432/tableflow}
      CORS_ALLOW_ALL_ORIGINS: "True"
    volumes:
      - media_data:/app/media
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  media_data:
```

- [ ] **Step 3: Ensure .env is in .gitignore**

Check `/Users/deuterium/Dev/TableFlow/.gitignore` — add `.env` if not present:

```bash
grep -q "^\.env$" /Users/deuterium/Dev/TableFlow/.gitignore || echo ".env" >> /Users/deuterium/Dev/TableFlow/.gitignore
```

- [ ] **Step 4: Smoke test with Docker Compose**

```bash
cd /Users/deuterium/Dev/TableFlow && cp .env.example .env
docker compose up -d --build 2>&1 | tail -20
```

Wait for containers to start:
```bash
sleep 15 && docker compose ps
```

Expected: all 3 services `running (healthy)` or `Up`.

Test the API:
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access','FAILED'))")
echo "Token: ${TOKEN:0:20}..."
```

Note: On first run the database is empty — the seed data lives only in the SQLite db. After compose up, run seed manually:
```bash
docker compose exec backend python manage.py shell -c "
from apps.accounts.models import User
from apps.restaurants.models import Restaurant
from apps.tables.models import Table
from apps.payments.models import PaymentMethod
from apps.menu.models import Category, Product

if not Restaurant.objects.exists():
    r = Restaurant.objects.create(name='TableFlow Demo', address='ул. Примерная, 1', phone='+7999000001', email='demo@tableflow.ru', currency='RUB')
    User.objects.create_superuser('admin', 'admin@tableflow.ru', 'admin123', role='admin', restaurant=r)
    for i in range(1, 11):
        Table.objects.create(restaurant=r, number=i, capacity=4)
    PaymentMethod.objects.create(name='Наличные')
    PaymentMethod.objects.create(name='Банковская карта')
    PaymentMethod.objects.create(name='QR-код')
    cat1 = Category.objects.create(name='Горячие блюда', restaurant=r, sort_order=1)
    cat2 = Category.objects.create(name='Напитки', restaurant=r, sort_order=2)
    for name, price, cat in [('Стейк рибай','1200.00',cat1),('Паста карбонара','450.00',cat1),('Кофе','180.00',cat2),('Чай','120.00',cat2)]:
        Product.objects.create(name=name, price=price, category=cat, restaurant=r, status='available')
    print('Seed OK')
"
```

Tear down after test:
```bash
docker compose down
```

- [ ] **Step 5: Commit**

```bash
cd /Users/deuterium/Dev/TableFlow && git add docker-compose.yml .env.example .gitignore && git commit -m "feat: add Docker Compose with postgres, backend, frontend services"
```

---

## Task 5: Kubernetes manifests

**Files:** All in `k8s/`

- [ ] **Step 1: Create k8s/namespace.yaml**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tableflow
```

- [ ] **Step 2: Create k8s/postgres/secret.yaml**

Values are base64-encoded. `tableflow` → `dGFibGVmbG93`, `tableflow_prod_password` → `dGFibGVmbG93X3Byb2RfcGFzc3dvcmQ=`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: tableflow
type: Opaque
data:
  # echo -n 'tableflow' | base64
  POSTGRES_DB: dGFibGVmbG93
  POSTGRES_USER: dGFibGVmbG93
  # echo -n 'tableflow_prod_password' | base64
  POSTGRES_PASSWORD: dGFibGVmbG93X3Byb2RfcGFzc3dvcmQ=
  # echo -n 'postgresql://tableflow:tableflow_prod_password@postgres:5432/tableflow' | base64
  DATABASE_URL: cG9zdGdyZXNxbDovL3RhYmxlZmxvdzp0YWJsZWZsb3dfcHJvZF9wYXNzd29yZEBwb3N0Z3Jlczs1NDMyL3RhYmxlZmxvdw==
```

> **Note for production:** Replace these values with actual secrets using `kubectl create secret` or a secrets manager. Never commit real credentials.

- [ ] **Step 3: Create k8s/postgres/pvc.yaml**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: tableflow
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

- [ ] **Step 4: Create k8s/postgres/deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: tableflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          ports:
            - containerPort: 5432
          envFrom:
            - secretRef:
                name: postgres-secret
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
          readinessProbe:
            exec:
              command: ["pg_isready", "-U", "tableflow"]
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-pvc
```

- [ ] **Step 5: Create k8s/postgres/service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: tableflow
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
  type: ClusterIP
```

- [ ] **Step 6: Create k8s/backend/secret.yaml**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secret
  namespace: tableflow
type: Opaque
data:
  # echo -n 'your-production-secret-key-here' | base64
  SECRET_KEY: eW91ci1wcm9kdWN0aW9uLXNlY3JldC1rZXktaGVyZQ==
  # Same as postgres-secret DATABASE_URL
  DATABASE_URL: cG9zdGdyZXNxbDovL3RhYmxlZmxvdzp0YWJsZWZsb3dfcHJvZF9wYXNzd29yZEBwb3N0Z3Jlczs1NDMyL3RhYmxlZmxvdw==
```

- [ ] **Step 7: Create k8s/backend/configmap.yaml**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
  namespace: tableflow
data:
  DEBUG: "False"
  ALLOWED_HOSTS: "localhost,tableflow.example.com"
  CORS_ALLOW_ALL_ORIGINS: "False"
  CORS_ALLOWED_ORIGINS: "https://tableflow.example.com"
```

- [ ] **Step 8: Create k8s/backend/deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: tableflow
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: tableflow-backend:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: backend-config
            - secretRef:
                name: backend-secret
          readinessProbe:
            httpGet:
              path: /api/auth/token/
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 10
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /api/auth/token/
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 30
          volumeMounts:
            - name: media-storage
              mountPath: /app/media
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
      volumes:
        - name: media-storage
          emptyDir: {}
```

- [ ] **Step 9: Create k8s/backend/service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: tableflow
spec:
  selector:
    app: backend
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP
```

- [ ] **Step 10: Create k8s/frontend/deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: tableflow
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: tableflow-frontend:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 80
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 30
          resources:
            requests:
              memory: "64Mi"
              cpu: "50m"
            limits:
              memory: "128Mi"
              cpu: "200m"
```

- [ ] **Step 11: Create k8s/frontend/service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: tableflow
spec:
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 80
  type: ClusterIP
```

- [ ] **Step 12: Create k8s/ingress.yaml**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tableflow-ingress
  namespace: tableflow
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "120"
spec:
  ingressClassName: nginx
  rules:
    - host: tableflow.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
          - path: /admin
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
          - path: /media
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 80
```

- [ ] **Step 13: Validate manifests (dry-run)**

If `kubectl` is available and a cluster is configured:
```bash
kubectl apply --dry-run=client -f /Users/deuterium/Dev/TableFlow/k8s/ --recursive 2>&1
```

If no cluster is available, validate YAML syntax:
```bash
find /Users/deuterium/Dev/TableFlow/k8s -name "*.yaml" | xargs -I{} python3 -c "import yaml,sys; yaml.safe_load_all(open('{}'))" && echo "All YAML valid"
```

Expected: no errors.

- [ ] **Step 14: Create k8s/README.md with deployment instructions**

```markdown
# Kubernetes Deployment

## Prerequisites
- kubectl configured for your cluster
- Docker images built and pushed to a registry

## Build & Push Images

```bash
# Set your registry
REGISTRY=your-registry.io/tableflow

docker build -t $REGISTRY/backend:latest ./backend
docker build -t $REGISTRY/frontend:latest ./frontend

docker push $REGISTRY/backend:latest
docker push $REGISTRY/frontend:latest
```

Update `image:` fields in `k8s/backend/deployment.yaml` and `k8s/frontend/deployment.yaml`.

## Deploy

```bash
# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/ingress.yaml
```

## Seed initial data (first deploy only)

```bash
POD=$(kubectl get pod -n tableflow -l app=backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n tableflow $POD -- python manage.py shell -c "
from apps.accounts.models import User
from apps.restaurants.models import Restaurant
from apps.tables.models import Table
from apps.payments.models import PaymentMethod
from apps.menu.models import Category, Product

if not Restaurant.objects.exists():
    r = Restaurant.objects.create(name='TableFlow', address='ул. Примерная, 1', phone='+7000000000', email='admin@tableflow.ru', currency='RUB')
    User.objects.create_superuser('admin', 'admin@tableflow.ru', 'CHANGE_ME', role='admin', restaurant=r)
    for i in range(1, 11):
        Table.objects.create(restaurant=r, number=i, capacity=4)
    PaymentMethod.objects.create(name='Наличные')
    PaymentMethod.objects.create(name='Банковская карта')
    print('Seed OK')
"
```

## Update secrets for production

```bash
kubectl create secret generic backend-secret \
  --from-literal=SECRET_KEY='your-real-secret-key' \
  --from-literal=DATABASE_URL='postgresql://user:pass@postgres:5432/tableflow' \
  -n tableflow --dry-run=client -o yaml | kubectl apply -f -
```
```

- [ ] **Step 15: Commit**

```bash
cd /Users/deuterium/Dev/TableFlow && git add k8s/ && git commit -m "feat: add Kubernetes manifests for namespace, postgres, backend, frontend, ingress"
```

---

## Self-Review

- [x] **Spec coverage:** Docker (backend + frontend Dockerfiles, compose), Kubernetes (all components).
- [x] **Placeholder scan:** No TBDs. Secrets have note about replacing for production.
- [x] **Type consistency:** Service names `backend`/`postgres`/`frontend` used consistently across ingress, nginx proxy, and compose.
- [x] **DATABASE_URL base64** — the value in postgres/secret.yaml matches the one in backend/secret.yaml.
- [x] **nginx.conf** proxies `/api/` to `http://backend:8000` matching the compose service name and K8s service name.
- [x] **entrypoint.sh** runs migrate before gunicorn — required for zero-downtime rolling deploys in K8s.
- [x] **ReadWriteOnce PVC** — correct for single-replica Postgres. Multi-replica Postgres needs ReadWriteMany or a managed DB.
