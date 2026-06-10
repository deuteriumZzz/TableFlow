# Code Cleanup + Shared `api` App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 4 known bugs, remove dead code, create a shared `apps/api` app with permissions/mixins/pagination/filters/serializers/health/seed, add drf-spectacular Swagger docs, and wire everything together.

**Architecture:** New `apps.api` Django app holds shared utilities (permissions, mixins, pagination, filters, serializers) consumed by all other apps; avoids duplicated code and establishes a single source of truth for cross-cutting concerns. Bug fixes are isolated model/view edits that require no structural change.

**Tech Stack:** Django 4.2, DRF 3.14, drf-spectacular 0.27.2, django-filter 24.3

---

## File Map

**Create:**
- `backend/apps/api/__init__.py`
- `backend/apps/api/apps.py`
- `backend/apps/api/mixins.py`
- `backend/apps/api/permissions.py`
- `backend/apps/api/pagination.py`
- `backend/apps/api/filters.py`
- `backend/apps/api/serializers.py`
- `backend/apps/api/health.py`
- `backend/apps/api/urls.py`
- `backend/apps/api/management/__init__.py`
- `backend/apps/api/management/commands/__init__.py`
- `backend/apps/api/management/commands/seed.py`
- `backend/apps/orders/filters.py`

**Modify:**
- `backend/apps/accounts/models.py` — remove duplicate `is_active`, remove `Session` model
- `backend/apps/reports/views.py` — check `is_valid()` return value
- `backend/apps/orders/models.py` — remove `partial` from `PAYMENT_STATUS_CHOICES`, add `recalculate_total()`
- `backend/apps/orders/views.py` — use `recalculate_total()`, use `OrderFilter`, use `StandardPagination`
- `backend/apps/menu/views.py` — use `api.permissions.IsStaffOrReadOnly`
- `backend/apps/staff/views.py` — use `api.permissions.IsManagerOrAdmin`
- `backend/config/settings.py` — add `apps.api`, `drf_spectacular`, `django_filters`
- `backend/config/urls.py` — add health URL, add swagger URLs
- `backend/requirements.txt` — add `drf-spectacular`, `django-filter`

**Delete:**
- `backend/apps/accounts/services/auth_service.py`
- `backend/apps/menu/permissions.py` (replaced by `api.permissions`)
- `backend/apps/staff/permissions.py` (replaced by `api.permissions`)

**Migration needed:**
- `backend/apps/accounts/migrations/0002_remove_session_is_active_duplicate.py` — auto-generated

---

### Task 1: Fix `accounts/models.py` — remove duplicate `is_active` and `Session` model

**Files:**
- Modify: `backend/apps/accounts/models.py`

- [ ] **Step 1: Read the current file to confirm line numbers**

```
backend/apps/accounts/models.py
```

Current state (relevant lines):
```python
class User(AbstractUser):
    ...
    is_active = models.BooleanField(default=True)      # ~line 17 — REMOVE, AbstractUser already has this
    last_login_pos = models.DateTimeField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='accounts/avatars/', blank=True)
    is_active = models.BooleanField(default=True)      # ~line 24 — REMOVE, duplicate

class Session(models.Model):                           # REMOVE entire class — unused
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
```

- [ ] **Step 2: Write the fixed `accounts/models.py`**

Replace the entire file with:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('cashier', 'Кассир'),
        ('waiter', 'Официант'),
        ('chef', 'Повар'),
        ('auditor', 'Аудитор'),
        ('client', 'Клиент'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    last_login_pos = models.DateTimeField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='accounts/avatars/', blank=True)
```

Note: `is_active` is inherited from `AbstractUser` — no need to declare it.

- [ ] **Step 3: Create migration to drop `Session` table**

```bash
cd backend
python manage.py makemigrations accounts --name remove_session_model
```

Expected output:
```
Migrations for 'accounts':
  apps/accounts/migrations/0002_remove_session_model.py
    - Delete model Session
    - Alter field is_active on user  (or similar — accept whatever Django generates)
```

- [ ] **Step 4: Run migration to verify it applies cleanly**

```bash
python manage.py migrate accounts
```

Expected output:
```
Running migrations:
  Applying accounts.0002_remove_session_model... OK
```

- [ ] **Step 5: Commit**

```bash
git add backend/apps/accounts/models.py backend/apps/accounts/migrations/0002_remove_session_model.py
git commit -m "fix: remove duplicate is_active and unused Session model from accounts"
```

---

### Task 2: Remove dead code

**Files:**
- Delete: `backend/apps/accounts/services/auth_service.py`

- [ ] **Step 1: Confirm nothing imports `auth_service.py`**

```bash
grep -r "auth_service" backend/ --include="*.py"
```

Expected: no output (nothing imports it).

- [ ] **Step 2: Delete the file**

```bash
rm backend/apps/accounts/services/auth_service.py
```

- [ ] **Step 3: Remove the now-empty `services/` directory if empty**

```bash
rmdir backend/apps/accounts/services/ 2>/dev/null || true
```

- [ ] **Step 4: Commit**

```bash
git add -u backend/apps/accounts/services/
git commit -m "chore: delete unused AuthService dead code"
```

---

### Task 3: Fix `reports/views.py` — check `is_valid()` return value

**Files:**
- Modify: `backend/apps/reports/views.py`

- [ ] **Step 1: Read the current file**

```
backend/apps/reports/views.py
```

Current problem:
```python
serializer = SalesReportSerializer(data=data)
serializer.is_valid()            # return value ignored — validation errors silently discarded
return Response(serializer.data) # may return empty/wrong data on validation failure
```

- [ ] **Step 2: Fix both views to raise on invalid data**

Replace the entire file with:

```python
from datetime import date as date_type

from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ProductReportSerializer, SalesReportSerializer
from .utils import generate_product_report, generate_sales_report


class SalesReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        date_str = request.query_params.get('date')
        if date_str:
            try:
                report_date = date_type.fromisoformat(date_str)
            except ValueError:
                return Response({'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, status=400)
        else:
            report_date = timezone.now().date()

        data = generate_sales_report(report_date)
        serializer = SalesReportSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class ProductReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id):
        date_str = request.query_params.get('date')
        if date_str:
            try:
                report_date = date_type.fromisoformat(date_str)
            except ValueError:
                return Response({'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, status=400)
        else:
            report_date = timezone.now().date()

        data = generate_product_report(product_id, report_date)
        serializer = ProductReportSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
```

- [ ] **Step 3: Commit**

```bash
git add backend/apps/reports/views.py
git commit -m "fix: raise on invalid serializer data in reports views"
```

---

### Task 4: Fix `Order.PAYMENT_STATUS_CHOICES` and add `recalculate_total()`

**Files:**
- Modify: `backend/apps/orders/models.py`

- [ ] **Step 1: Read the current orders/models.py**

```
backend/apps/orders/models.py
```

- [ ] **Step 2: Remove `partial` from PAYMENT_STATUS_CHOICES and add `recalculate_total()`**

The `partial` status is unreachable because `Payment` uses `OneToOneField` to `Order` — only one payment per order is possible. Remove it to prevent dead states.

Replace `orders/models.py` with:

```python
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('in_progress', 'В обработке'),
        ('ready', 'Готов'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
        ('refunded', 'Возврат'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидание оплаты'),
        ('paid', 'Оплачен'),
        ('failed', 'Оплата не удалась'),
        ('refunded', 'Возврат средств'),
    ]

    table = models.ForeignKey(
        'tables.Table', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Стол"),
    )
    user = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Пользователь"),
    )
    waitress = models.ForeignKey(
        'accounts.User', related_name='orders_as_waitress',
        on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Официант"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создан"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='created',
        verbose_name=_("Статус"),
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending',
        verbose_name=_("Статус оплаты"),
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name=_("Итоговая сумма"),
    )
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name=_("Скидка"),
    )
    tax = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name=_("Налог"),
    )
    comment = models.TextField(blank=True, verbose_name=_("Комментарий"))
    is_online = models.BooleanField(default=False, verbose_name=_("Онлайн-заказ"))
    restaurant = models.ForeignKey(
        'restaurants.Restaurant', on_delete=models.CASCADE,
        verbose_name=_("Ресторан"),
    )

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.status} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def recalculate_total(self):
        """Recompute total_amount from current items and persist."""
        self.total_amount = sum(item.total_price for item in self.items.all())
        self.save(update_fields=['total_amount'])


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items',
        verbose_name=_("Заказ"),
    )
    product = models.ForeignKey(
        'menu.Product', on_delete=models.SET_NULL, null=True,
        verbose_name=_("Товар"),
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Количество"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Цена за единицу"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Итоговая цена"))
    comment = models.TextField(blank=True, verbose_name=_("Комментарий"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создан"))
    status = models.CharField(max_length=20, default='pending', verbose_name=_("Статус"))
    modifiers = models.ManyToManyField(
        'menu.Modifier', through='OrderItemModifier', blank=True,
        verbose_name=_("Модификаторы"),
    )

    class Meta:
        verbose_name = _("Позиция заказа")
        verbose_name_plural = _("Позиции заказов")


class OrderItemModifier(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    modifier = models.ForeignKey('menu.Modifier', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _("Модификатор позиции заказа")
        verbose_name_plural = _("Модификаторы позиций заказов")
```

- [ ] **Step 3: Create migration for removed `partial` choice**

```bash
cd backend
python manage.py makemigrations orders --name remove_partial_payment_status
```

Expected output:
```
Migrations for 'orders':
  apps/orders/migrations/0002_remove_partial_payment_status.py
    - Alter field payment_status on order
```

- [ ] **Step 4: Apply migration**

```bash
python manage.py migrate orders
```

- [ ] **Step 5: Update `orders/views.py` to use `recalculate_total()`**

In `backend/apps/orders/views.py`, replace the two manual total calculations:

Old pattern (appears twice):
```python
order.total_amount = sum(i.total_price for i in order.items.all())
order.save()
```

New pattern:
```python
order.recalculate_total()
```

The full updated `add_item` action tail and `remove_item` action tail:
```python
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        order = self.get_object()
        if order.status not in ('created', 'in_progress'):
            return Response(
                {'error': 'Нельзя добавить позицию в заказ с текущим статусом'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = AddItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        product = get_object_or_404(
            Product, id=data['product_id'],
            restaurant=request.user.restaurant, is_active=True,
        )
        modifier_price = Decimal('0')
        modifiers = []
        for mid in data.get('modifier_ids', []):
            m = get_object_or_404(Modifier, id=mid, restaurant=request.user.restaurant)
            modifier_price += m.price
            modifiers.append(m)

        unit_price = product.price + modifier_price
        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=data['quantity'],
            price=unit_price,
            total_price=unit_price * data['quantity'],
            comment=data.get('comment', ''),
        )
        for m in modifiers:
            OrderItemModifier.objects.create(order_item=item, modifier=m, quantity=1)

        order.recalculate_total()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['delete'], url_path=r'remove_item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, pk=None, item_id=None):
        order = self.get_object()
        item = get_object_or_404(OrderItem, id=item_id, order=order)
        item.delete()
        order.recalculate_total()
        return Response(OrderSerializer(order).data)
```

- [ ] **Step 6: Commit**

```bash
git add backend/apps/orders/models.py backend/apps/orders/migrations/0002_remove_partial_payment_status.py backend/apps/orders/views.py
git commit -m "fix: remove unreachable partial payment status; add Order.recalculate_total()"
```

---

### Task 5: Create `apps/api/` — foundation files

**Files:**
- Create: `backend/apps/api/__init__.py`
- Create: `backend/apps/api/apps.py`

- [ ] **Step 1: Create `apps/api/__init__.py`**

```python
# backend/apps/api/__init__.py
```
(empty file)

- [ ] **Step 2: Create `apps/api/apps.py`**

```python
from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.api'
    verbose_name = 'API'
```

- [ ] **Step 3: Register in `config/settings.py`**

Add `'apps.api'` to `INSTALLED_APPS` after the existing apps:
```python
INSTALLED_APPS = [
    ...
    'apps.reports',
    'apps.api',       # <-- add this line
]
```

- [ ] **Step 4: Commit**

```bash
git add backend/apps/api/ backend/config/settings.py
git commit -m "feat: scaffold apps.api app"
```

---

### Task 6: Add `api/permissions.py` — unified permissions

**Files:**
- Create: `backend/apps/api/permissions.py`
- Modify: `backend/apps/menu/views.py`
- Modify: `backend/apps/staff/views.py`
- Delete: `backend/apps/menu/permissions.py`
- Delete: `backend/apps/staff/permissions.py`

- [ ] **Step 1: Create `backend/apps/api/permissions.py`**

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role == 'manager'
        )


class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role in ('admin', 'manager')
        )


class IsStaffOrReadOnly(BasePermission):
    """Allow read to any authenticated user; write only to admin/manager/cashier."""
    WRITE_ROLES = ('admin', 'manager', 'cashier')

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in self.WRITE_ROLES


class IsCashierOrAbove(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role in ('admin', 'manager', 'cashier')
        )
```

- [ ] **Step 2: Update `backend/apps/menu/views.py`**

Replace the import line:
```python
# OLD
from .permissions import IsStaffOrReadOnly

# NEW
from apps.api.permissions import IsStaffOrReadOnly
```

- [ ] **Step 3: Update `backend/apps/staff/views.py`**

Replace the import line:
```python
# OLD
from .permissions import IsManagerOrAdmin

# NEW
from apps.api.permissions import IsManagerOrAdmin
```

- [ ] **Step 4: Delete old permissions files**

```bash
rm backend/apps/menu/permissions.py
rm backend/apps/staff/permissions.py
```

- [ ] **Step 5: Verify no remaining imports of old permission modules**

```bash
grep -r "from .permissions import\|from apps.menu.permissions\|from apps.staff.permissions" backend/ --include="*.py"
```

Expected: no output.

- [ ] **Step 6: Commit**

```bash
git add backend/apps/api/permissions.py backend/apps/menu/views.py backend/apps/staff/views.py
git rm backend/apps/menu/permissions.py backend/apps/staff/permissions.py
git commit -m "refactor: consolidate permissions into apps.api.permissions"
```

---

### Task 7: Add `api/mixins.py` and `api/pagination.py`

**Files:**
- Create: `backend/apps/api/mixins.py`
- Create: `backend/apps/api/pagination.py`
- Modify: `backend/apps/orders/views.py`

- [ ] **Step 1: Create `backend/apps/api/mixins.py`**

```python
class RestaurantMixin:
    """
    Scopes ViewSet queryset and creates to the authenticated user's restaurant.
    Use as the first base class: class MyViewSet(RestaurantMixin, viewsets.ModelViewSet)
    """

    def get_queryset(self):
        return super().get_queryset().filter(
            restaurant=self.request.user.restaurant
        )

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurant)
```

- [ ] **Step 2: Create `backend/apps/api/pagination.py`**

```python
from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Default pagination: 25 items per page, max 100."""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargePagination(PageNumberPagination):
    """For lists that are typically large: 100 items per page, max 500."""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500
```

- [ ] **Step 3: Apply `StandardPagination` to `OrderViewSet`**

In `backend/apps/orders/views.py`, add the import and set the class attribute:

```python
# Add to imports at top of file:
from apps.api.pagination import StandardPagination

# Add to OrderViewSet class body (after permission_classes):
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    ...
```

- [ ] **Step 4: Commit**

```bash
git add backend/apps/api/mixins.py backend/apps/api/pagination.py backend/apps/orders/views.py
git commit -m "feat: add RestaurantMixin, StandardPagination/LargePagination to api app; paginate OrderViewSet"
```

---

### Task 8: Add `api/filters.py`, `api/serializers.py`, and `orders/filters.py`

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/apps/api/filters.py`
- Create: `backend/apps/api/serializers.py`
- Create: `backend/apps/orders/filters.py`
- Modify: `backend/apps/orders/views.py`
- Modify: `backend/config/settings.py`

- [ ] **Step 1: Add `django-filter` to `backend/requirements.txt`**

Add this line:
```
django-filter==24.3
```

- [ ] **Step 2: Add `django_filters` to `INSTALLED_APPS` and configure DRF filter backend**

In `backend/config/settings.py`, add to `INSTALLED_APPS`:
```python
'django_filters',
```

Add to `REST_FRAMEWORK` dict:
```python
'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
```

- [ ] **Step 3: Create `backend/apps/api/filters.py`**

```python
import django_filters


class BaseRestaurantFilter(django_filters.FilterSet):
    """
    Base FilterSet for restaurant-scoped models.
    Extend this in each app's filters.py:

        class OrderFilter(BaseRestaurantFilter):
            class Meta:
                model = Order
                fields = ['status']
    """

    class Meta:
        abstract = True
```

- [ ] **Step 4: Create `backend/apps/api/serializers.py`**

```python
from rest_framework import serializers


class TimestampedSerializer(serializers.ModelSerializer):
    """Base serializer that marks created_at/updated_at as read-only."""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class WritableNestedMixin:
    """
    Mixin that provides a helper for writable nested serializers.
    Usage: call self.create_or_update_nested(parent, field_name, data, ChildSerializer)
    """

    def create_or_update_nested(self, parent, field_name, items_data, child_serializer_class):
        getattr(parent, field_name).all().delete()
        for item_data in items_data:
            child_serializer_class.objects.create(**item_data, **{parent._meta.model_name: parent})
```

- [ ] **Step 5: Create `backend/apps/orders/filters.py`**

```python
import django_filters

from apps.api.filters import BaseRestaurantFilter
from .models import Order


class OrderFilter(BaseRestaurantFilter):
    status = django_filters.CharFilter()
    date_from = django_filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='created_at__date', lookup_expr='lte')

    class Meta:
        model = Order
        fields = ['status', 'date_from', 'date_to']
```

- [ ] **Step 6: Wire `OrderFilter` into `OrderViewSet`**

In `backend/apps/orders/views.py`, add at the top:
```python
from django_filters.rest_framework import DjangoFilterBackend
from .filters import OrderFilter
```

Add to `OrderViewSet` class:
```python
filter_backends = [DjangoFilterBackend]
filterset_class = OrderFilter
```

And remove the manual `query_params.get('status')` filter block from `get_queryset`:
```python
def get_queryset(self):
    return Order.objects.filter(
        restaurant=self.request.user.restaurant
    ).prefetch_related('items__product', 'items__modifiers')
    # status filtering now handled by OrderFilter
```

- [ ] **Step 7: Install dependencies and verify import**

```bash
cd backend
pip install django-filter==24.3
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 8: Commit**

```bash
git add backend/requirements.txt backend/config/settings.py \
        backend/apps/api/filters.py backend/apps/api/serializers.py \
        backend/apps/orders/filters.py backend/apps/orders/views.py
git commit -m "feat: add api/filters.py, api/serializers.py; wire django-filter into OrderViewSet"
```

---

### Task 9: Add `api/health.py` health-check endpoint

**Files:**
- Create: `backend/apps/api/health.py`
- Create: `backend/apps/api/urls.py`
- Modify: `backend/config/urls.py`

- [ ] **Step 1: Create `backend/apps/api/health.py`**

```python
from django.db import connection, OperationalError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    try:
        connection.ensure_connection()
        db_ok = True
    except OperationalError:
        db_ok = False

    http_status = 200 if db_ok else 503
    return Response(
        {'status': 'ok' if db_ok else 'degraded', 'db': db_ok},
        status=http_status,
    )
```

- [ ] **Step 2: Create `backend/apps/api/urls.py`**

```python
from django.urls import path

from .health import health_check

urlpatterns = [
    path('health/', health_check, name='health'),
]
```

- [ ] **Step 3: Register in `backend/config/urls.py`**

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),          # <-- add this line FIRST
    path('api/', include('apps.accounts.urls')),
    ...
] + static(...)
```

- [ ] **Step 4: Test the endpoint**

```bash
cd backend
python manage.py runserver &
sleep 2
curl -s http://localhost:8000/api/health/
```

Expected:
```json
{"status": "ok", "db": true}
```

Kill the server: `kill %1`

- [ ] **Step 5: Update K8s liveness/readiness probes to use health endpoint**

In `k8s/backend/deployment.yaml`, replace the probe paths:
```yaml
readinessProbe:
  httpGet:
    path: /api/health/
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  failureThreshold: 3
livenessProbe:
  httpGet:
    path: /api/health/
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 30
```

- [ ] **Step 6: Commit**

```bash
git add backend/apps/api/health.py backend/apps/api/urls.py \
        backend/config/urls.py k8s/backend/deployment.yaml
git commit -m "feat: add /api/health/ endpoint; update K8s probes"
```

---

### Task 10: Add `drf-spectacular` Swagger/OpenAPI documentation

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/config/settings.py`
- Modify: `backend/config/urls.py`

- [ ] **Step 1: Add to `backend/requirements.txt`**

```
drf-spectacular==0.27.2
```

- [ ] **Step 2: Update `backend/config/settings.py`**

Add `'drf_spectacular'` to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'apps.api',
    'drf_spectacular',   # <-- add
]
```

Add to `REST_FRAMEWORK` dict:
```python
REST_FRAMEWORK = {
    ...
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

Add new settings block at the bottom of the file:
```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'TableFlow API',
    'DESCRIPTION': 'POS-система для ресторанов — REST API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

- [ ] **Step 3: Add Swagger URLs to `backend/config/urls.py`**

```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include('apps.accounts.urls')),
    ...
] + static(...)
```

- [ ] **Step 4: Install and verify**

```bash
cd backend
pip install drf-spectacular==0.27.2
python manage.py spectacular --validate --fail-on-warn
```

Expected:
```
Schema generation succeeded without errors/warnings.
```

- [ ] **Step 5: Test Swagger UI in browser (if running locally)**

```bash
python manage.py runserver &
sleep 2
curl -s http://localhost:8000/api/docs/ | grep -o "<title>.*</title>"
```

Expected: `<title>Swagger UI</title>` or similar.

Kill: `kill %1`

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/config/settings.py backend/config/urls.py
git commit -m "feat: add drf-spectacular OpenAPI/Swagger docs at /api/docs/"
```

---

### Task 11: Add seed management command

**Files:**
- Create: `backend/apps/api/management/__init__.py`
- Create: `backend/apps/api/management/commands/__init__.py`
- Create: `backend/apps/api/management/commands/seed.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p backend/apps/api/management/commands
touch backend/apps/api/management/__init__.py
touch backend/apps/api/management/commands/__init__.py
```

- [ ] **Step 2: Create `backend/apps/api/management/commands/seed.py`**

```python
from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.menu.models import Category, Product
from apps.payments.models import PaymentMethod
from apps.restaurants.models import Restaurant
from apps.tables.models import Table


class Command(BaseCommand):
    help = 'Seed the database with demo data for development'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        restaurant, _ = Restaurant.objects.get_or_create(
            name='Demo Restaurant',
            defaults={
                'address': 'ул. Примерная, д. 1',
                'phone': '+7 (999) 000-00-00',
                'is_active': True,
            },
        )
        self.stdout.write(f'  Restaurant: {restaurant.name}')

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='admin',
                restaurant=restaurant,
            )
            self.stdout.write('  User: admin / admin123 (admin)')

        if not User.objects.filter(username='manager').exists():
            User.objects.create_user(
                username='manager',
                email='manager@example.com',
                password='manager123',
                role='manager',
                restaurant=restaurant,
            )
            self.stdout.write('  User: manager / manager123 (manager)')

        if not User.objects.filter(username='waiter').exists():
            User.objects.create_user(
                username='waiter',
                email='waiter@example.com',
                password='waiter123',
                role='waiter',
                restaurant=restaurant,
            )
            self.stdout.write('  User: waiter / waiter123 (waiter)')

        for number in range(1, 11):
            Table.objects.get_or_create(
                restaurant=restaurant,
                number=number,
                defaults={'capacity': 4, 'status': 'free'},
            )
        self.stdout.write('  Tables: 1–10 created')

        cat_main, _ = Category.objects.get_or_create(
            name='Основные блюда', restaurant=restaurant,
            defaults={'sort_order': 1, 'is_active': True},
        )
        cat_drinks, _ = Category.objects.get_or_create(
            name='Напитки', restaurant=restaurant,
            defaults={'sort_order': 2, 'is_active': True},
        )

        menu_items = [
            ('Борщ', '350.00', cat_main),
            ('Пельмени', '290.00', cat_main),
            ('Салат Цезарь', '280.00', cat_main),
            ('Стейк', '850.00', cat_main),
            ('Чай', '80.00', cat_drinks),
            ('Кофе', '120.00', cat_drinks),
            ('Апельсиновый сок', '150.00', cat_drinks),
            ('Вода', '60.00', cat_drinks),
        ]
        for name, price, category in menu_items:
            Product.objects.get_or_create(
                name=name,
                restaurant=restaurant,
                defaults={
                    'price': price,
                    'category': category,
                    'is_active': True,
                    'status': 'available',
                },
            )
        self.stdout.write(f'  Products: {len(menu_items)} created')

        for method_name in ['Наличные', 'Карта', 'QR-код']:
            PaymentMethod.objects.get_or_create(name=method_name)
        self.stdout.write('  Payment methods: Наличные, Карта, QR-код')

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
```

- [ ] **Step 3: Test the command**

```bash
cd backend
python manage.py seed
```

Expected output:
```
Seeding database...
  Restaurant: Demo Restaurant
  User: admin / admin123 (admin)
  User: manager / manager123 (manager)
  User: waiter / waiter123 (waiter)
  Tables: 1–10 created
  Products: 8 created
  Payment methods: Наличные, Карта, QR-код
Seed complete.
```

Run again to verify idempotency (no duplicate errors):
```bash
python manage.py seed
```

Expected: same output, no errors.

- [ ] **Step 4: Add seed to `entrypoint.sh` for Docker dev (optional — only if DEBUG=True)**

In `backend/entrypoint.sh`, after `migrate` and before `gunicorn`, add:
```bash
if [ "$DEBUG" = "True" ]; then
    python manage.py seed
fi
```

- [ ] **Step 5: Commit**

```bash
git add backend/apps/api/management/ backend/entrypoint.sh
git commit -m "feat: add seed management command with demo restaurant, users, tables, menu, payment methods"
```

---

### Task 12: Final wiring check

- [ ] **Step 1: Verify all imports resolve**

```bash
cd backend
python manage.py check --deploy 2>&1 | grep -v "WARNINGS"
```

Or without `--deploy` for dev:
```bash
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 2: Run all migrations cleanly**

```bash
python manage.py migrate
```

Expected: all migrations applied, no errors.

- [ ] **Step 3: Smoke-test the server**

```bash
python manage.py runserver &
sleep 2
curl -s http://localhost:8000/api/health/   # → {"status":"ok","db":true}
curl -s http://localhost:8000/api/docs/ | grep -c "swagger"  # → 1 or more
kill %1
```

- [ ] **Step 4: Final commit**

```bash
git add -u
git commit -m "chore: final wiring — all apps.api utilities integrated"
```
