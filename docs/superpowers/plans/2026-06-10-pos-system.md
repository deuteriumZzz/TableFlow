# POS System (TableFlow) — Full Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete a full-stack restaurant POS system — Django REST API backend + React/TypeScript frontend for table management, order taking, and payment processing.

**Architecture:** Django 4.2 + DRF + simplejwt handles all API endpoints with JWT auth; React 18 + Vite frontend serves the POS GUI; Zustand manages client-side state; all Django apps live under `apps/` and are registered as `apps.<name>` in INSTALLED_APPS.

**Tech Stack:** Django 4.2, djangorestframework 3.14, djangorestframework-simplejwt 5.3, django-cors-headers 4.3, Pillow 10; React 18, TypeScript 5, Vite 5, Tailwind CSS 3, Zustand 4, Axios 1, React Router 6

---

## File Map

### Backend — new/modified
```
backend/
  requirements.txt                           CREATE
  config/settings.py                         MODIFY — add DRF, JWT, CORS, INSTALLED_APPS
  config/urls.py                             MODIFY — add all API routes

  apps/accounts/apps.py                      MODIFY — name = "apps.accounts"
  apps/accounts/serializers.py               MODIFY — fix CustomTokenSerializer
  apps/accounts/views.py                     MODIFY — add /me endpoint
  apps/accounts/urls.py                      CREATE
  apps/accounts/services/auth_service.py     MODIFY — fix import path

  apps/restaurants/apps.py                   CREATE — AppConfig
  apps/restaurants/admin.py                  CREATE
  apps/restaurants/serializers.py            CREATE
  apps/restaurants/views.py                  CREATE
  apps/restaurants/urls.py                   CREATE

  apps/tables/__init__.py                    CREATE
  apps/tables/apps.py                        CREATE
  apps/tables/models.py                      CREATE
  apps/tables/admin.py                       CREATE
  apps/tables/serializers.py                 CREATE
  apps/tables/views.py                       CREATE
  apps/tables/urls.py                        CREATE

  apps/menu/apps.py                          MODIFY — name = "apps.menu"
  apps/menu/views.py                         MODIFY — fix perform_create, add restaurant filter
  apps/menu/models.py                        MODIFY — add modifiers M2M to Product
  apps/menu/urls.py                          CREATE

  apps/orders/apps.py                        MODIFY — name = "apps.orders"
  apps/orders/serializers.py                 CREATE
  apps/orders/views.py                       REPLACE — was empty
  apps/orders/urls.py                        CREATE

  apps/payments/apps.py                      MODIFY — name = "apps.payments"
  apps/payments/models.py                    MODIFY — fix import path
  apps/payments/views.py                     MODIFY — fix logic, add list endpoint
  apps/payments/urls.py                      CREATE

  apps/staff/apps.py                         MODIFY — name = "apps.staff"
  apps/staff/models.py                       MODIFY — fix import paths
  apps/staff/permissions.py                  CREATE — IsManagerOrAdmin
  apps/staff/urls.py                         CREATE

  apps/reports/apps.py                       MODIFY — name = "apps.reports"
  apps/reports/serializers.py               REPLACE — proper DRF serializers
  apps/reports/views.py                      MODIFY — fix missing imports, fix Response usage
  apps/reports/urls.py                       CREATE
```

### Frontend — all new
```
frontend/
  package.json
  vite.config.ts
  tsconfig.json
  index.html
  tailwind.config.js
  postcss.config.js
  src/
    main.tsx
    App.tsx
    types/index.ts
    api/
      client.ts
      auth.ts
      tables.ts
      menu.ts
      orders.ts
      payments.ts
    store/
      authStore.ts
      posStore.ts
    pages/
      LoginPage.tsx
      TablesPage.tsx
      POSPage.tsx
      KitchenPage.tsx
    components/
      PrivateRoute.tsx
      TableGrid.tsx
      CategoryTabs.tsx
      ProductCard.tsx
      MenuPanel.tsx
      OrderItemRow.tsx
      OrderPanel.tsx
      PaymentModal.tsx
      StatusBadge.tsx
```

---

## Task 1: Install dependencies + fix settings.py

**Files:**
- Create: `backend/requirements.txt`
- Modify: `backend/config/settings.py`

- [ ] **Step 1: Create requirements.txt**

```
# backend/requirements.txt
Django==4.2.30
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
Pillow==10.4.0
sqlparse==0.5.5
asgiref==3.11.1
```

- [ ] **Step 2: Install requirements**

```bash
cd /path/to/TableFlow
source venv/bin/activate
pip install -r backend/requirements.txt
```

Expected: all packages install without error.

- [ ] **Step 3: Replace settings.py**

```python
# backend/config/settings.py
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-!b5&*m=!m_wl_cf936cs@v6r#1m7(pgws!w*5)*4iy&mc4m5av'
DEBUG = True
ALLOWED_HOSTS = ['*']

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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

CORS_ALLOW_ALL_ORIGINS = True
```

- [ ] **Step 4: Verify Django can load settings**

```bash
cd backend && python manage.py check --deploy 2>&1 | head -20
```

Expected: warnings only (no errors about missing apps/modules).

---

## Task 2: Fix AppConfig names in all apps.py

**Files:** Modify `apps.py` in accounts, menu, orders, payments, staff, reports. Create for restaurants.

- [ ] **Step 1: Fix accounts/apps.py**

```python
# backend/apps/accounts/apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
```

- [ ] **Step 2: Fix menu/apps.py**

```python
# backend/apps/menu/apps.py
from django.apps import AppConfig

class MenuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.menu'
```

- [ ] **Step 3: Fix orders/apps.py**

```python
# backend/apps/orders/apps.py
from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
```

- [ ] **Step 4: Fix payments/apps.py**

```python
# backend/apps/payments/apps.py
from django.apps import AppConfig

class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments'
```

- [ ] **Step 5: Fix staff/apps.py**

```python
# backend/apps/staff/apps.py
from django.apps import AppConfig

class StaffConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.staff'
```

- [ ] **Step 6: Fix reports/apps.py**

```python
# backend/apps/reports/apps.py
from django.apps import AppConfig

class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reports'
```

- [ ] **Step 7: Create restaurants/apps.py**

```python
# backend/apps/restaurants/apps.py
from django.apps import AppConfig

class RestaurantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.restaurants'
```

- [ ] **Step 8: Verify Django recognizes apps**

```bash
cd backend && python manage.py check 2>&1
```

Expected: `System check identified no issues (0 silenced).` or only minor warnings.

---

## Task 3: Fix cross-app imports + broken references

**Files:** Modify `payments/models.py`, `staff/models.py`, `accounts/services/auth_service.py`, `reports/utils.py`

- [ ] **Step 1: Fix payments/models.py**

```python
# backend/apps/payments/models.py
from django.db import models
from apps.orders.models import Order

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидание'),
        ('success', 'Успешно'),
        ('failed', 'Не удалось'),
        ('refunded', 'Возврат'),
    )

    order = models.OneToOneField(Order, related_name='payment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Платеж #{self.id} за заказ #{self.order.id}"
```

- [ ] **Step 2: Fix staff/models.py**

```python
# backend/apps/staff/models.py
from django.db import models
from apps.accounts.models import User
from apps.restaurants.models import Restaurant

class StaffSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.day} {self.start_time}-{self.end_time}"

class StaffSalary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Зарплата {self.user.username} за {self.month}"
```

- [ ] **Step 3: Fix auth_service.py**

```python
# backend/apps/accounts/services/auth_service.py
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from apps.accounts.models import User

class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        user = authenticate(username=username, password=password)
        if user:
            user.last_login_pos = timezone.now()
            user.save()
        return user

    @staticmethod
    def create_user(data):
        user = User(
            username=data['username'],
            email=data['email'],
            password=make_password(data['password']),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data.get('role', 'cashier'),
        )
        user.save()
        return user
```

- [ ] **Step 4: Fix reports/utils.py**

```python
# backend/apps/reports/utils.py
from django.db.models import Sum, Count
from apps.orders.models import Order, OrderItem

def generate_sales_report(date):
    orders = Order.objects.filter(
        created_at__date=date,
        status='delivered',
        payment_status='paid',
    )
    total_orders = orders.count()
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    return {
        'date': str(date),
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
    }

def generate_product_report(product_id, date):
    row = OrderItem.objects.filter(
        product_id=product_id,
        order__created_at__date=date,
        order__status='delivered',
    ).aggregate(
        quantity_sold=Count('id'),
        total_revenue=Sum('total_price'),
    )
    return {
        'product_id': product_id,
        'date': str(date),
        'quantity_sold': row['quantity_sold'] or 0,
        'total_revenue': float(row['total_revenue'] or 0),
    }
```

- [ ] **Step 5: Verify no import errors**

```bash
cd backend && python manage.py check 2>&1
```

Expected: 0 errors.

---

## Task 4: Create tables app

**Files:** Create all files in `backend/apps/tables/`

- [ ] **Step 1: Create `__init__.py`**

```python
# backend/apps/tables/__init__.py
```

(empty file)

- [ ] **Step 2: Create apps.py**

```python
# backend/apps/tables/apps.py
from django.apps import AppConfig

class TablesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tables'
```

- [ ] **Step 3: Create models.py**

```python
# backend/apps/tables/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class Table(models.Model):
    STATUS_CHOICES = [
        ('free', 'Свободен'),
        ('occupied', 'Занят'),
        ('reserved', 'Забронирован'),
    ]

    restaurant = models.ForeignKey(
        'restaurants.Restaurant', on_delete=models.CASCADE,
        related_name='tables', verbose_name=_('Ресторан')
    )
    number = models.PositiveIntegerField(verbose_name=_('Номер стола'))
    capacity = models.PositiveIntegerField(default=4, verbose_name=_('Вместимость'))
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='free',
        verbose_name=_('Статус')
    )

    class Meta:
        verbose_name = _('Стол')
        verbose_name_plural = _('Столы')
        unique_together = ('restaurant', 'number')
        ordering = ['number']

    def __str__(self):
        return f"Стол #{self.number} ({self.get_status_display()})"
```

- [ ] **Step 4: Create admin.py**

```python
# backend/apps/tables/admin.py
from django.contrib import admin
from .models import Table

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'restaurant', 'capacity', 'status']
    list_filter = ['status', 'restaurant']
```

- [ ] **Step 5: Create serializers.py**

```python
# backend/apps/tables/serializers.py
from rest_framework import serializers
from .models import Table

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'number', 'capacity', 'status', 'restaurant']
        read_only_fields = ['restaurant']
```

- [ ] **Step 6: Create views.py**

```python
# backend/apps/tables/views.py
from rest_framework import viewsets, permissions
from .models import Table
from .serializers import TableSerializer

class TableViewSet(viewsets.ModelViewSet):
    serializer_class = TableSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Table.objects.filter(restaurant=self.request.user.restaurant)

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurant)
```

- [ ] **Step 7: Create urls.py**

```python
# backend/apps/tables/urls.py
from rest_framework.routers import DefaultRouter
from .views import TableViewSet

router = DefaultRouter()
router.register(r'tables', TableViewSet, basename='table')

urlpatterns = router.urls
```

- [ ] **Step 8: Verify model loads**

```bash
cd backend && python manage.py check 2>&1
```

Expected: 0 errors.

---

## Task 5: Complete restaurants app

**Files:** Create `restaurants/serializers.py`, `restaurants/views.py`, `restaurants/urls.py`, `restaurants/admin.py`. Add `__init__.py` if missing.

- [ ] **Step 1: Ensure `__init__.py` exists**

```python
# backend/apps/restaurants/__init__.py
```

- [ ] **Step 2: Create admin.py**

```python
# backend/apps/restaurants/admin.py
from django.contrib import admin
from .models import Restaurant

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'is_active', 'currency']
    list_filter = ['is_active']
```

- [ ] **Step 3: Create serializers.py**

```python
# backend/apps/restaurants/serializers.py
from rest_framework import serializers
from .models import Restaurant

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'phone', 'email', 'logo', 'is_active', 'currency']
```

- [ ] **Step 4: Create views.py**

```python
# backend/apps/restaurants/views.py
from rest_framework import viewsets, permissions
from .models import Restaurant
from .serializers import RestaurantSerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.filter(is_active=True)
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]
```

- [ ] **Step 5: Create urls.py**

```python
# backend/apps/restaurants/urls.py
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')

urlpatterns = router.urls
```

---

## Task 6: Fix accounts app

**Files:** Modify `accounts/serializers.py`, `accounts/views.py`, create `accounts/urls.py`

- [ ] **Step 1: Replace serializers.py**

```python
# backend/apps/accounts/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['restaurant_id'] = user.restaurant_id
        return token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'role', 'phone', 'avatar', 'is_active', 'restaurant']
        read_only_fields = ['is_active', 'restaurant']
```

- [ ] **Step 2: Replace views.py**

```python
# backend/apps/accounts/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from .models import User

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role in ('admin', 'manager'):
            return User.objects.filter(restaurant=self.request.user.restaurant)
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        return Response(UserSerializer(request.user).data)
```

- [ ] **Step 3: Create urls.py**

```python
# backend/apps/accounts/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls
```

---

## Task 7: Add modifiers M2M to Product + complete menu app

**Files:** Modify `menu/models.py`, `menu/views.py`, create `menu/urls.py`

- [ ] **Step 1: Add modifiers M2M field to Product**

In `backend/apps/menu/models.py`, add to the `Product` class (after the `updated_at` field):

```python
    modifiers = models.ManyToManyField(
        'Modifier', through='ProductModifier', blank=True,
        verbose_name=_('Модификаторы')
    )
```

The full Product model with the addition:

```python
class Product(models.Model):
    STATUS_CHOICES = [
        ('available', 'В наличии'),
        ('out_of_stock', 'Нет в наличии'),
        ('limited', 'Ограниченное количество'),
    ]

    name = models.CharField(max_length=200, verbose_name=_('Название'))
    description = models.TextField(blank=True, verbose_name=_('Описание'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Категория'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена'))
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Себестоимость'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name=_('Статус'))
    image = models.ImageField(upload_to='menu_products/', blank=True, verbose_name=_('Изображение'))
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, verbose_name=_('Ресторан'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активен'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))
    min_stock = models.PositiveIntegerField(default=0, verbose_name=_('Минимальный остаток'))
    current_stock = models.PositiveIntegerField(default=0, verbose_name=_('Текущий остаток'))
    modifiers = models.ManyToManyField('Modifier', through='ProductModifier', blank=True, verbose_name=_('Модификаторы'))

    class Meta:
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')
        ordering = ['name']
```

- [ ] **Step 2: Fix menu/views.py**

```python
# backend/apps/menu/views.py
from rest_framework import viewsets, permissions
from .models import Product, Category, Modifier
from .serializers import ProductSerializer, CategorySerializer, ModifierSerializer
from .permissions import IsStaffOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        return Category.objects.filter(
            restaurant=self.request.user.restaurant,
            is_active=True,
        )

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurant)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = Product.objects.filter(
            restaurant=self.request.user.restaurant,
            is_active=True,
        )
        category_id = self.request.query_params.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurant)

class ModifierViewSet(viewsets.ModelViewSet):
    serializer_class = ModifierSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        return Modifier.objects.filter(restaurant=self.request.user.restaurant)

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurant)
```

- [ ] **Step 3: Create menu/urls.py**

```python
# backend/apps/menu/urls.py
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ModifierViewSet

router = DefaultRouter()
router.register(r'menu/categories', CategoryViewSet, basename='category')
router.register(r'menu/products', ProductViewSet, basename='product')
router.register(r'menu/modifiers', ModifierViewSet, basename='modifier')

urlpatterns = router.urls
```

---

## Task 8: Complete orders app (serializers + views + urls)

This is the core of the POS system.

**Files:** Create `orders/serializers.py`, replace `orders/views.py`, create `orders/urls.py`

- [ ] **Step 1: Create orders/serializers.py**

```python
# backend/apps/orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem, OrderItemModifier
from apps.menu.serializers import ProductSerializer, ModifierSerializer

class OrderItemModifierSerializer(serializers.ModelSerializer):
    modifier = ModifierSerializer(read_only=True)

    class Meta:
        model = OrderItemModifier
        fields = ['id', 'modifier', 'quantity']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    applied_modifiers = OrderItemModifierSerializer(
        source='orderitemmodifier_set', many=True, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_price',
                  'comment', 'status', 'applied_modifiers']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    table_number = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'table', 'table_number', 'waitress', 'status', 'payment_status',
                  'total_amount', 'discount', 'tax', 'comment', 'is_online',
                  'created_at', 'updated_at', 'items']
        read_only_fields = ['total_amount', 'created_at', 'updated_at',
                            'waitress', 'restaurant']

    def get_table_number(self, obj):
        return obj.table.number if obj.table else None

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['table', 'comment', 'is_online']

    def create(self, validated_data):
        validated_data['restaurant'] = self.context['request'].user.restaurant
        validated_data['waitress'] = self.context['request'].user
        return super().create(validated_data)

class AddItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    comment = serializers.CharField(required=False, allow_blank=True, default='')
    modifier_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=list
    )
```

- [ ] **Step 2: Create orders/views.py**

```python
# backend/apps/orders/views.py
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem, OrderItemModifier
from .serializers import OrderSerializer, OrderCreateSerializer, AddItemSerializer
from apps.menu.models import Product, Modifier
from apps.tables.models import Table

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        qs = Order.objects.filter(
            restaurant=self.request.user.restaurant
        ).prefetch_related('items__product', 'items__modifiers')
        order_status = self.request.query_params.get('status')
        if order_status:
            qs = qs.filter(status=order_status)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        if order.table:
            order.table.status = 'occupied'
            order.table.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

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
            restaurant=request.user.restaurant, is_active=True
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

        order.total_amount = sum(i.total_price for i in order.items.all())
        order.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['delete'], url_path='remove_item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, pk=None, item_id=None):
        order = self.get_object()
        item = get_object_or_404(OrderItem, id=item_id, order=order)
        item.delete()
        order.total_amount = sum(i.total_price for i in order.items.all())
        order.save()
        return Response(OrderSerializer(order).data)

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
        return Response(OrderSerializer(order).data)
```

- [ ] **Step 3: Create orders/urls.py**

```python
# backend/apps/orders/urls.py
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = router.urls
```

---

## Task 9: Complete payments app

**Files:** Modify `payments/views.py`, create `payments/urls.py`

- [ ] **Step 1: Replace payments/views.py**

```python
# backend/apps/payments/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .models import Payment, PaymentMethod
from .serializers import PaymentSerializer, PaymentMethodSerializer
from apps.orders.models import Order

class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            order__restaurant=self.request.user.restaurant
        )

    def create(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        method_id = request.data.get('method_id')
        try:
            order = Order.objects.get(
                id=order_id,
                restaurant=request.user.restaurant,
            )
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(order, 'payment'):
            return Response(
                {'error': 'Заказ уже оплачен'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            method_id=method_id,
            status='success',
        )
        order.payment_status = 'paid'
        order.status = 'delivered'
        order.save()
        if order.table:
            order.table.status = 'free'
            order.table.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
```

- [ ] **Step 2: Add PaymentMethodSerializer to payments/serializers.py**

```python
# backend/apps/payments/serializers.py
from rest_framework import serializers
from .models import Payment, PaymentMethod

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'description']

class PaymentSerializer(serializers.ModelSerializer):
    method_name = serializers.CharField(source='method.name', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'method', 'method_name',
                  'status', 'transaction_id', 'created_at']
        read_only_fields = ['created_at']
```

- [ ] **Step 3: Create payments/urls.py**

```python
# backend/apps/payments/urls.py
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentMethodViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')

urlpatterns = router.urls
```

---

## Task 10: Fix staff app

**Files:** Create `staff/permissions.py`, create `staff/urls.py`

- [ ] **Step 1: Create staff/permissions.py**

```python
# backend/apps/staff/permissions.py
from rest_framework import permissions

class IsManagerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ('admin', 'manager')
        )
```

- [ ] **Step 2: Create staff/urls.py**

```python
# backend/apps/staff/urls.py
from rest_framework.routers import DefaultRouter
from .views import StaffScheduleViewSet, StaffSalaryViewSet

router = DefaultRouter()
router.register(r'staff/schedules', StaffScheduleViewSet, basename='staff-schedule')
router.register(r'staff/salaries', StaffSalaryViewSet, basename='staff-salary')

urlpatterns = router.urls
```

---

## Task 11: Fix reports app

**Files:** Replace `reports/serializers.py`, fix `reports/views.py`, create `reports/urls.py`

- [ ] **Step 1: Replace reports/serializers.py**

```python
# backend/apps/reports/serializers.py
from rest_framework import serializers

class SalesReportSerializer(serializers.Serializer):
    date = serializers.CharField()
    total_orders = serializers.IntegerField()
    total_revenue = serializers.FloatField()

class ProductReportSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    date = serializers.CharField()
    quantity_sold = serializers.IntegerField()
    total_revenue = serializers.FloatField()
```

- [ ] **Step 2: Replace reports/views.py**

```python
# backend/apps/reports/views.py
from django.utils import timezone
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from .serializers import SalesReportSerializer, ProductReportSerializer
from .utils import generate_sales_report, generate_product_report

class SalesReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        date_str = request.query_params.get('date')
        if date_str:
            from datetime import date
            try:
                report_date = date.fromisoformat(date_str)
            except ValueError:
                return Response({'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, status=400)
        else:
            report_date = timezone.now().date()
        data = generate_sales_report(report_date)
        serializer = SalesReportSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data)

class ProductReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id):
        date_str = request.query_params.get('date')
        if date_str:
            from datetime import date
            try:
                report_date = date.fromisoformat(date_str)
            except ValueError:
                return Response({'error': 'Неверный формат даты'}, status=400)
        else:
            report_date = timezone.now().date()
        data = generate_product_report(product_id, report_date)
        serializer = ProductReportSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data)
```

- [ ] **Step 3: Create reports/urls.py**

```python
# backend/apps/reports/urls.py
from django.urls import path
from .views import SalesReportView, ProductReportView

urlpatterns = [
    path('reports/sales/', SalesReportView.as_view(), name='report-sales'),
    path('reports/products/<int:product_id>/', ProductReportView.as_view(), name='report-product'),
]
```

---

## Task 12: Wire config/urls.py

**Files:** Replace `backend/config/urls.py`

- [ ] **Step 1: Replace config/urls.py**

```python
# backend/config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.restaurants.urls')),
    path('api/', include('apps.tables.urls')),
    path('api/', include('apps.menu.urls')),
    path('api/', include('apps.orders.urls')),
    path('api/', include('apps.payments.urls')),
    path('api/', include('apps.staff.urls')),
    path('api/', include('apps.reports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

- [ ] **Step 2: Verify all URLs resolve**

```bash
cd backend && python manage.py show_urls 2>/dev/null | head -40 || python manage.py check 2>&1
```

Expected: no errors; list of URLs including `/api/auth/token/`, `/api/orders/`, etc.

---

## Task 13: Run migrations + seed data

- [ ] **Step 1: Generate migrations for all apps**

```bash
cd backend && python manage.py makemigrations accounts restaurants tables menu orders payments staff reports
```

Expected: migration files created in each app's `migrations/` directory.

- [ ] **Step 2: Run migrations**

```bash
cd backend && python manage.py migrate
```

Expected: all migrations applied successfully.

- [ ] **Step 3: Create superuser + seed data**

```bash
cd backend && python manage.py shell -c "
from apps.accounts.models import User
from apps.restaurants.models import Restaurant
from apps.tables.models import Table
from apps.payments.models import PaymentMethod

r = Restaurant.objects.create(name='TableFlow Demo', address='ул. Примерная, 1', phone='+7999000001', email='demo@tableflow.ru', currency='RUB')
User.objects.create_superuser('admin', 'admin@tableflow.ru', 'admin123', role='admin', restaurant=r)
User.objects.create_user('waiter1', 'waiter@tableflow.ru', 'waiter123', role='waiter', restaurant=r, first_name='Иван')
for i in range(1, 11):
    Table.objects.create(restaurant=r, number=i, capacity=4)
PaymentMethod.objects.create(name='Наличные')
PaymentMethod.objects.create(name='Банковская карта')
PaymentMethod.objects.create(name='QR-код')
print('Seed data created')
"
```

Expected: `Seed data created`

- [ ] **Step 4: Verify API works**

```bash
cd backend && python manage.py runserver &
sleep 3
curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python -m json.tool
```

Expected: JSON response with `access` and `refresh` tokens.

```bash
kill %1 2>/dev/null; true
```

---

## Task 14: Frontend project setup

**Files:** Create all config files in `frontend/`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "tableflow-pos",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.7.2",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.24.0",
    "zustand": "^4.5.2"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.39",
    "tailwindcss": "^3.4.4",
    "typescript": "^5.5.3",
    "vite": "^5.3.1"
  }
}
```

- [ ] **Step 2: Create vite.config.ts**

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 4: Create tsconfig.node.json**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 5: Create index.html**

```html
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>TableFlow POS</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 6: Create tailwind.config.js**

```javascript
// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: { extend: {} },
  plugins: [],
}
```

- [ ] **Step 7: Create postcss.config.js**

```javascript
// frontend/postcss.config.js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 8: Install dependencies**

```bash
cd frontend && npm install
```

Expected: `node_modules` created, no errors.

---

## Task 15: TypeScript types + API client

**Files:** Create `src/types/index.ts`, `src/api/client.ts`, `src/api/auth.ts`, `src/api/tables.ts`, `src/api/menu.ts`, `src/api/orders.ts`, `src/api/payments.ts`

- [ ] **Step 1: Create src/types/index.ts**

```typescript
// frontend/src/types/index.ts
export interface Restaurant {
  id: number
  name: string
  currency: string
}

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: 'admin' | 'manager' | 'cashier' | 'waiter' | 'chef' | 'auditor' | 'client'
  restaurant: number | null
  phone: string
  avatar: string | null
}

export interface Table {
  id: number
  number: number
  capacity: number
  status: 'free' | 'occupied' | 'reserved'
  restaurant: number
}

export interface Category {
  id: number
  name: string
  description: string
  image: string | null
  sort_order: number
}

export interface Modifier {
  id: number
  name: string
  price: string
  is_required: boolean
}

export interface Product {
  id: number
  name: string
  description: string
  price: string
  status: 'available' | 'out_of_stock' | 'limited'
  image: string | null
  category: Category | null
  modifiers: Modifier[]
}

export interface OrderItemModifier {
  id: number
  modifier: Modifier
  quantity: number
}

export interface OrderItem {
  id: number
  product: Product
  quantity: number
  price: string
  total_price: string
  comment: string
  status: string
  applied_modifiers: OrderItemModifier[]
}

export type OrderStatus = 'created' | 'in_progress' | 'ready' | 'delivered' | 'cancelled' | 'refunded'
export type PaymentStatus = 'pending' | 'paid' | 'partial' | 'failed' | 'refunded'

export interface Order {
  id: number
  table: number | null
  table_number: number | null
  waitress: number | null
  status: OrderStatus
  payment_status: PaymentStatus
  total_amount: string
  discount: string
  tax: string
  comment: string
  is_online: boolean
  created_at: string
  updated_at: string
  items: OrderItem[]
}

export interface PaymentMethod {
  id: number
  name: string
  description: string
}

export interface Payment {
  id: number
  order: number
  amount: string
  method: number
  method_name: string
  status: string
  transaction_id: string
  created_at: string
}

export interface AuthTokens {
  access: string
  refresh: string
}
```

- [ ] **Step 2: Create src/api/client.ts**

```typescript
// frontend/src/api/client.ts
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post('/api/auth/token/refresh/', { refresh })
          localStorage.setItem('access_token', data.access)
          original.headers.Authorization = `Bearer ${data.access}`
          return client(original)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  },
)

export default client
```

- [ ] **Step 3: Create src/api/auth.ts**

```typescript
// frontend/src/api/auth.ts
import client from './client'
import axios from 'axios'
import type { User, AuthTokens } from '../types'

export const login = async (username: string, password: string): Promise<AuthTokens> => {
  const { data } = await axios.post<AuthTokens>('/api/auth/token/', { username, password })
  return data
}

export const getMe = async (): Promise<User> => {
  const { data } = await client.get<User>('/users/me/')
  return data
}
```

- [ ] **Step 4: Create src/api/tables.ts**

```typescript
// frontend/src/api/tables.ts
import client from './client'
import type { Table } from '../types'

export const getTables = async (): Promise<Table[]> => {
  const { data } = await client.get<{ results: Table[] }>('/tables/')
  return data.results ?? data
}

export const updateTableStatus = async (
  id: number,
  tableStatus: Table['status'],
): Promise<Table> => {
  const { data } = await client.patch<Table>(`/tables/${id}/`, { status: tableStatus })
  return data
}
```

- [ ] **Step 5: Create src/api/menu.ts**

```typescript
// frontend/src/api/menu.ts
import client from './client'
import type { Category, Product } from '../types'

export const getCategories = async (): Promise<Category[]> => {
  const { data } = await client.get<{ results: Category[] }>('/menu/categories/')
  return data.results ?? data
}

export const getProducts = async (categoryId?: number): Promise<Product[]> => {
  const params = categoryId ? { category: categoryId } : {}
  const { data } = await client.get<{ results: Product[] }>('/menu/products/', { params })
  return data.results ?? data
}
```

- [ ] **Step 6: Create src/api/orders.ts**

```typescript
// frontend/src/api/orders.ts
import client from './client'
import type { Order, OrderStatus } from '../types'

export const getOrders = async (orderStatus?: OrderStatus): Promise<Order[]> => {
  const params = orderStatus ? { status: orderStatus } : {}
  const { data } = await client.get<{ results: Order[] }>('/orders/', { params })
  return data.results ?? data
}

export const getOrder = async (id: number): Promise<Order> => {
  const { data } = await client.get<Order>(`/orders/${id}/`)
  return data
}

export const createOrder = async (tableId: number | null, comment = ''): Promise<Order> => {
  const { data } = await client.post<Order>('/orders/', { table: tableId, comment })
  return data
}

export const addItem = async (
  orderId: number,
  productId: number,
  quantity: number,
  comment = '',
  modifierIds: number[] = [],
): Promise<Order> => {
  const { data } = await client.post<Order>(`/orders/${orderId}/add_item/`, {
    product_id: productId,
    quantity,
    comment,
    modifier_ids: modifierIds,
  })
  return data
}

export const removeItem = async (orderId: number, itemId: number): Promise<Order> => {
  const { data } = await client.delete<Order>(`/orders/${orderId}/remove_item/${itemId}/`)
  return data
}

export const updateOrderStatus = async (orderId: number, newStatus: OrderStatus): Promise<Order> => {
  const { data } = await client.post<Order>(`/orders/${orderId}/update_status/`, { status: newStatus })
  return data
}
```

- [ ] **Step 7: Create src/api/payments.ts**

```typescript
// frontend/src/api/payments.ts
import client from './client'
import type { Payment, PaymentMethod } from '../types'

export const getPaymentMethods = async (): Promise<PaymentMethod[]> => {
  const { data } = await client.get<{ results: PaymentMethod[] }>('/payment-methods/')
  return data.results ?? data
}

export const createPayment = async (orderId: number, methodId: number): Promise<Payment> => {
  const { data } = await client.post<Payment>('/payments/', {
    order_id: orderId,
    method_id: methodId,
  })
  return data
}
```

---

## Task 16: Zustand stores

**Files:** Create `src/store/authStore.ts`, `src/store/posStore.ts`

- [ ] **Step 1: Create src/store/authStore.ts**

```typescript
// frontend/src/store/authStore.ts
import { create } from 'zustand'
import type { User } from '../types'
import { login as apiLogin, getMe } from '../api/auth'

interface AuthState {
  user: User | null
  isLoading: boolean
  error: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: false,
  error: null,

  login: async (username, password) => {
    set({ isLoading: true, error: null })
    try {
      const tokens = await apiLogin(username, password)
      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      const user = await getMe()
      set({ user, isLoading: false })
    } catch {
      set({ error: 'Неверный логин или пароль', isLoading: false })
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null })
  },

  loadUser: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) return
    try {
      const user = await getMe()
      set({ user })
    } catch {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  },
}))
```

- [ ] **Step 2: Create src/store/posStore.ts**

```typescript
// frontend/src/store/posStore.ts
import { create } from 'zustand'
import type { Table, Order, Category, Product } from '../types'
import * as ordersApi from '../api/orders'

interface PosState {
  selectedTable: Table | null
  currentOrder: Order | null
  categories: Category[]
  products: Product[]
  selectedCategoryId: number | null
  paymentModalOpen: boolean

  selectTable: (table: Table) => void
  clearTable: () => void
  setOrder: (order: Order) => void
  setCategories: (cats: Category[]) => void
  setProducts: (prods: Product[]) => void
  selectCategory: (id: number | null) => void
  openPayment: () => void
  closePayment: () => void
  addItem: (productId: number, quantity: number, comment?: string) => Promise<void>
  removeItem: (itemId: number) => Promise<void>
}

export const usePosStore = create<PosState>((set, get) => ({
  selectedTable: null,
  currentOrder: null,
  categories: [],
  products: [],
  selectedCategoryId: null,
  paymentModalOpen: false,

  selectTable: (table) => set({ selectedTable: table }),
  clearTable: () => set({ selectedTable: null, currentOrder: null }),

  setOrder: (order) => set({ currentOrder: order }),
  setCategories: (cats) => set({ categories: cats }),
  setProducts: (prods) => set({ products: prods }),
  selectCategory: (id) => set({ selectedCategoryId: id }),
  openPayment: () => set({ paymentModalOpen: true }),
  closePayment: () => set({ paymentModalOpen: false }),

  addItem: async (productId, quantity, comment = '') => {
    const { currentOrder } = get()
    if (!currentOrder) return
    const updated = await ordersApi.addItem(currentOrder.id, productId, quantity, comment)
    set({ currentOrder: updated })
  },

  removeItem: async (itemId) => {
    const { currentOrder } = get()
    if (!currentOrder) return
    const updated = await ordersApi.removeItem(currentOrder.id, itemId)
    set({ currentOrder: updated })
  },
}))
```

---

## Task 17: App shell + routing

**Files:** Create `src/main.tsx`, `src/App.tsx`, `src/components/PrivateRoute.tsx`, global CSS

- [ ] **Step 1: Create src/index.css**

```css
/* frontend/src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  @apply bg-gray-100 text-gray-900;
}
```

- [ ] **Step 2: Create src/main.tsx**

```tsx
// frontend/src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

- [ ] **Step 3: Create src/components/PrivateRoute.tsx**

```tsx
// frontend/src/components/PrivateRoute.tsx
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function PrivateRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user)
  const token = localStorage.getItem('access_token')
  if (!token && !user) return <Navigate to="/login" replace />
  return <>{children}</>
}
```

- [ ] **Step 4: Create src/App.tsx**

```tsx
// frontend/src/App.tsx
import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import PrivateRoute from './components/PrivateRoute'
import LoginPage from './pages/LoginPage'
import TablesPage from './pages/TablesPage'
import POSPage from './pages/POSPage'
import KitchenPage from './pages/KitchenPage'

export default function App() {
  const loadUser = useAuthStore((s) => s.loadUser)

  useEffect(() => {
    loadUser()
  }, [loadUser])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <TablesPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/pos/:tableId"
          element={
            <PrivateRoute>
              <POSPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/kitchen"
          element={
            <PrivateRoute>
              <KitchenPage />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
```

---

## Task 18: Login page

**Files:** Create `src/pages/LoginPage.tsx`

- [ ] **Step 1: Create LoginPage.tsx**

```tsx
// frontend/src/pages/LoginPage.tsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const { login, isLoading, error, user } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (user) navigate('/')
  }, [user, navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await login(username, password)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-sm">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-2">TableFlow</h1>
        <p className="text-center text-gray-500 mb-8 text-sm">POS-система для ресторана</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Логин</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="admin"
              required
              autoFocus
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••"
              required
            />
          </div>

          {error && (
            <p className="text-red-500 text-sm text-center">{error}</p>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition-colors"
          >
            {isLoading ? 'Вход...' : 'Войти'}
          </button>
        </form>
      </div>
    </div>
  )
}
```

---

## Task 19: Tables page

**Files:** Create `src/components/StatusBadge.tsx`, `src/components/TableGrid.tsx`, `src/pages/TablesPage.tsx`

- [ ] **Step 1: Create src/components/StatusBadge.tsx**

```tsx
// frontend/src/components/StatusBadge.tsx
const STATUS_LABEL: Record<string, string> = {
  free: 'Свободен',
  occupied: 'Занят',
  reserved: 'Забронирован',
  created: 'Создан',
  in_progress: 'В работе',
  ready: 'Готов',
  delivered: 'Выдан',
  cancelled: 'Отменён',
  pending: 'Ожидание',
  paid: 'Оплачен',
  failed: 'Ошибка',
}

const STATUS_COLOR: Record<string, string> = {
  free: 'bg-green-100 text-green-800',
  occupied: 'bg-red-100 text-red-800',
  reserved: 'bg-yellow-100 text-yellow-800',
  created: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-orange-100 text-orange-800',
  ready: 'bg-green-100 text-green-800',
  delivered: 'bg-gray-100 text-gray-600',
  cancelled: 'bg-gray-100 text-gray-500',
  pending: 'bg-yellow-100 text-yellow-800',
  paid: 'bg-green-100 text-green-800',
}

export default function StatusBadge({ status }: { status: string }) {
  const color = STATUS_COLOR[status] ?? 'bg-gray-100 text-gray-600'
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {STATUS_LABEL[status] ?? status}
    </span>
  )
}
```

- [ ] **Step 2: Create src/components/TableGrid.tsx**

```tsx
// frontend/src/components/TableGrid.tsx
import type { Table } from '../types'

interface Props {
  tables: Table[]
  onSelect: (table: Table) => void
}

const TABLE_COLOR: Record<Table['status'], string> = {
  free: 'bg-green-500 hover:bg-green-600 text-white',
  occupied: 'bg-red-500 hover:bg-red-600 text-white',
  reserved: 'bg-yellow-500 hover:bg-yellow-600 text-white',
}

export default function TableGrid({ tables, onSelect }: Props) {
  if (tables.length === 0) {
    return (
      <p className="text-center text-gray-400 py-12">Нет столов. Добавьте их в панели администратора.</p>
    )
  }

  return (
    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-4">
      {tables.map((table) => (
        <button
          key={table.id}
          onClick={() => onSelect(table)}
          className={`${TABLE_COLOR[table.status]} rounded-2xl p-5 flex flex-col items-center justify-center shadow transition-transform hover:scale-105 active:scale-95`}
        >
          <span className="text-3xl font-bold">#{table.number}</span>
          <span className="text-sm mt-1 opacity-90">
            {table.status === 'free' ? `${table.capacity} мест` : table.status === 'occupied' ? 'Занят' : 'Бронь'}
          </span>
        </button>
      ))}
    </div>
  )
}
```

- [ ] **Step 3: Create src/pages/TablesPage.tsx**

```tsx
// frontend/src/pages/TablesPage.tsx
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { usePosStore } from '../store/posStore'
import { getTables } from '../api/tables'
import { createOrder } from '../api/orders'
import TableGrid from '../components/TableGrid'
import type { Table } from '../types'

export default function TablesPage() {
  const [tables, setTables] = useState<Table[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const { selectTable, setOrder } = usePosStore()
  const navigate = useNavigate()

  const load = async () => {
    try {
      const data = await getTables()
      setTables(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleSelectTable = async (table: Table) => {
    setCreating(true)
    try {
      selectTable(table)
      const order = await createOrder(table.id)
      setOrder(order)
      navigate(`/pos/${table.id}`)
    } finally {
      setCreating(false)
    }
  }

  const handleKitchen = () => navigate('/kitchen')

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-800">TableFlow POS</h1>
        <div className="flex items-center gap-4">
          <button
            onClick={handleKitchen}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Кухня
          </button>
          <span className="text-sm text-gray-500">{user?.first_name || user?.username}</span>
          <button
            onClick={logout}
            className="text-sm text-red-500 hover:text-red-700"
          >
            Выйти
          </button>
        </div>
      </header>

      <main className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-700">Выберите стол</h2>
          <button
            onClick={load}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Обновить
          </button>
        </div>

        {loading ? (
          <p className="text-center text-gray-400 py-12">Загрузка...</p>
        ) : (
          <TableGrid tables={tables} onSelect={handleSelectTable} />
        )}

        {creating && (
          <div className="fixed inset-0 bg-black/30 flex items-center justify-center">
            <div className="bg-white rounded-xl px-8 py-6 shadow-xl">
              <p className="text-gray-700">Создание заказа...</p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
```

---

## Task 20: Menu panel components

**Files:** Create `src/components/CategoryTabs.tsx`, `src/components/ProductCard.tsx`, `src/components/MenuPanel.tsx`

- [ ] **Step 1: Create src/components/CategoryTabs.tsx**

```tsx
// frontend/src/components/CategoryTabs.tsx
import type { Category } from '../types'

interface Props {
  categories: Category[]
  selected: number | null
  onSelect: (id: number | null) => void
}

export default function CategoryTabs({ categories, selected, onSelect }: Props) {
  return (
    <div className="flex gap-2 flex-wrap mb-4">
      <button
        onClick={() => onSelect(null)}
        className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
          selected === null
            ? 'bg-blue-600 text-white'
            : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
        }`}
      >
        Все
      </button>
      {categories.map((cat) => (
        <button
          key={cat.id}
          onClick={() => onSelect(cat.id)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            selected === cat.id
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
          }`}
        >
          {cat.name}
        </button>
      ))}
    </div>
  )
}
```

- [ ] **Step 2: Create src/components/ProductCard.tsx**

```tsx
// frontend/src/components/ProductCard.tsx
import type { Product } from '../types'

interface Props {
  product: Product
  onAdd: (product: Product) => void
}

export default function ProductCard({ product, onAdd }: Props) {
  const unavailable = product.status === 'out_of_stock'
  return (
    <button
      onClick={() => !unavailable && onAdd(product)}
      disabled={unavailable}
      className={`bg-white rounded-xl p-3 text-left shadow-sm border-2 transition-all ${
        unavailable
          ? 'opacity-50 cursor-not-allowed border-transparent'
          : 'border-transparent hover:border-blue-400 hover:shadow-md active:scale-95'
      }`}
    >
      {product.image ? (
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-24 object-cover rounded-lg mb-2"
        />
      ) : (
        <div className="w-full h-24 bg-gray-100 rounded-lg mb-2 flex items-center justify-center text-3xl">
          🍽
        </div>
      )}
      <p className="text-sm font-semibold text-gray-800 truncate">{product.name}</p>
      <p className="text-blue-600 font-bold mt-1">{parseFloat(product.price).toFixed(0)} ₽</p>
      {product.status === 'out_of_stock' && (
        <p className="text-red-400 text-xs mt-0.5">Нет в наличии</p>
      )}
    </button>
  )
}
```

- [ ] **Step 3: Create src/components/MenuPanel.tsx**

```tsx
// frontend/src/components/MenuPanel.tsx
import { useEffect } from 'react'
import { usePosStore } from '../store/posStore'
import { getCategories, getProducts } from '../api/menu'
import CategoryTabs from './CategoryTabs'
import ProductCard from './ProductCard'
import type { Product } from '../types'

interface Props {
  onAddProduct: (product: Product) => void
}

export default function MenuPanel({ onAddProduct }: Props) {
  const { categories, products, selectedCategoryId, setCategories, setProducts, selectCategory } =
    usePosStore()

  useEffect(() => {
    getCategories().then(setCategories)
  }, [setCategories])

  useEffect(() => {
    getProducts(selectedCategoryId ?? undefined).then(setProducts)
  }, [selectedCategoryId, setProducts])

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <CategoryTabs
        categories={categories}
        selected={selectedCategoryId}
        onSelect={selectCategory}
      />
      <div className="flex-1 overflow-y-auto">
        <div className="grid grid-cols-3 gap-3 pb-4">
          {products.map((p) => (
            <ProductCard key={p.id} product={p} onAdd={onAddProduct} />
          ))}
          {products.length === 0 && (
            <p className="col-span-3 text-center text-gray-400 py-8">Нет товаров</p>
          )}
        </div>
      </div>
    </div>
  )
}
```

---

## Task 21: Order panel components

**Files:** Create `src/components/OrderItemRow.tsx`, `src/components/OrderPanel.tsx`

- [ ] **Step 1: Create src/components/OrderItemRow.tsx**

```tsx
// frontend/src/components/OrderItemRow.tsx
import type { OrderItem } from '../types'

interface Props {
  item: OrderItem
  onRemove: (itemId: number) => void
}

export default function OrderItemRow({ item, onRemove }: Props) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-gray-100 last:border-0">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-800 truncate">{item.product.name}</p>
        {item.comment && <p className="text-xs text-gray-400">{item.comment}</p>}
        <p className="text-xs text-gray-500">×{item.quantity}</p>
      </div>
      <p className="text-sm font-semibold text-gray-800 whitespace-nowrap">
        {parseFloat(item.total_price).toFixed(0)} ₽
      </p>
      <button
        onClick={() => onRemove(item.id)}
        className="text-red-400 hover:text-red-600 text-lg leading-none ml-1"
        title="Удалить"
      >
        ×
      </button>
    </div>
  )
}
```

- [ ] **Step 2: Create src/components/OrderPanel.tsx**

```tsx
// frontend/src/components/OrderPanel.tsx
import { usePosStore } from '../store/posStore'
import OrderItemRow from './OrderItemRow'
import StatusBadge from './StatusBadge'

interface Props {
  onPay: () => void
  onClose: () => void
}

export default function OrderPanel({ onPay, onClose }: Props) {
  const { selectedTable, currentOrder, removeItem } = usePosStore()

  const total = currentOrder
    ? parseFloat(currentOrder.total_amount).toFixed(0)
    : '0'

  const canPay =
    currentOrder &&
    currentOrder.items.length > 0 &&
    currentOrder.payment_status === 'pending'

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="px-4 py-3 bg-gray-800 text-white flex items-center justify-between">
        <div>
          <p className="font-bold">
            {selectedTable ? `Стол #${selectedTable.number}` : 'Без стола'}
          </p>
          {currentOrder && (
            <p className="text-xs text-gray-300">Заказ #{currentOrder.id}</p>
          )}
        </div>
        {currentOrder && <StatusBadge status={currentOrder.status} />}
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-2">
        {!currentOrder || currentOrder.items.length === 0 ? (
          <p className="text-center text-gray-400 py-8 text-sm">Добавьте позиции из меню</p>
        ) : (
          currentOrder.items.map((item) => (
            <OrderItemRow
              key={item.id}
              item={item}
              onRemove={(id) => removeItem(id)}
            />
          ))
        )}
      </div>

      <div className="px-4 py-4 border-t border-gray-200 space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-gray-600 font-medium">Итого</span>
          <span className="text-2xl font-bold text-gray-800">{total} ₽</span>
        </div>
        <button
          onClick={onPay}
          disabled={!canPay}
          className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors text-lg"
        >
          Оплатить
        </button>
        <button
          onClick={onClose}
          className="w-full text-gray-500 hover:text-gray-700 text-sm py-1"
        >
          ← Вернуться к столам
        </button>
      </div>
    </div>
  )
}
```

---

## Task 22: POS page assembly

**Files:** Create `src/pages/POSPage.tsx`

- [ ] **Step 1: Create src/pages/POSPage.tsx**

```tsx
// frontend/src/pages/POSPage.tsx
import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { usePosStore } from '../store/posStore'
import MenuPanel from '../components/MenuPanel'
import OrderPanel from '../components/OrderPanel'
import PaymentModal from '../components/PaymentModal'
import type { Product } from '../types'

export default function POSPage() {
  const { tableId } = useParams<{ tableId: string }>()
  const navigate = useNavigate()
  const { selectedTable, currentOrder, addItem, openPayment, paymentModalOpen, clearTable } =
    usePosStore()

  useEffect(() => {
    if (!selectedTable) navigate('/')
  }, [selectedTable, navigate])

  const handleAddProduct = (product: Product) => {
    addItem(product.id, 1)
  }

  const handleClose = () => {
    clearTable()
    navigate('/')
  }

  return (
    <div className="h-screen flex bg-gray-100 overflow-hidden">
      <div className="flex-1 flex flex-col p-4 overflow-hidden">
        <h2 className="text-lg font-semibold text-gray-700 mb-3">
          Меню — Стол #{tableId}
        </h2>
        <div className="flex-1 overflow-hidden">
          <MenuPanel onAddProduct={handleAddProduct} />
        </div>
      </div>

      <div className="w-80 flex-shrink-0 p-4">
        <OrderPanel onPay={openPayment} onClose={handleClose} />
      </div>

      {paymentModalOpen && currentOrder && (
        <PaymentModal
          order={currentOrder}
          onClose={() => {
            usePosStore.getState().closePayment()
          }}
          onSuccess={() => {
            usePosStore.getState().closePayment()
            clearTable()
            navigate('/')
          }}
        />
      )}
    </div>
  )
}
```

---

## Task 23: Payment modal

**Files:** Create `src/components/PaymentModal.tsx`

- [ ] **Step 1: Create src/components/PaymentModal.tsx**

```tsx
// frontend/src/components/PaymentModal.tsx
import { useEffect, useState } from 'react'
import { getPaymentMethods, createPayment } from '../api/payments'
import type { Order, PaymentMethod } from '../types'

interface Props {
  order: Order
  onClose: () => void
  onSuccess: () => void
}

export default function PaymentModal({ order, onClose, onSuccess }: Props) {
  const [methods, setMethods] = useState<PaymentMethod[]>([])
  const [selectedMethod, setSelectedMethod] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getPaymentMethods().then((m) => {
      setMethods(m)
      if (m.length > 0) setSelectedMethod(m[0].id)
    })
  }, [])

  const handlePay = async () => {
    if (!selectedMethod) return
    setLoading(true)
    setError(null)
    try {
      await createPayment(order.id, selectedMethod)
      onSuccess()
    } catch {
      setError('Ошибка при проведении оплаты')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm mx-4">
        <h2 className="text-xl font-bold text-gray-800 mb-1">Оплата заказа</h2>
        <p className="text-gray-500 text-sm mb-5">Заказ #{order.id}</p>

        <div className="bg-gray-50 rounded-xl p-4 mb-5 flex justify-between items-center">
          <span className="text-gray-600">Сумма к оплате</span>
          <span className="text-2xl font-bold text-gray-900">
            {parseFloat(order.total_amount).toFixed(0)} ₽
          </span>
        </div>

        <p className="text-sm font-medium text-gray-700 mb-3">Способ оплаты</p>
        <div className="space-y-2 mb-6">
          {methods.map((m) => (
            <label
              key={m.id}
              className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-colors ${
                selectedMethod === m.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <input
                type="radio"
                name="method"
                value={m.id}
                checked={selectedMethod === m.id}
                onChange={() => setSelectedMethod(m.id)}
                className="accent-blue-600"
              />
              <span className="font-medium text-gray-800">{m.name}</span>
            </label>
          ))}
        </div>

        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 border border-gray-300 text-gray-700 font-medium py-3 rounded-xl hover:bg-gray-50 transition-colors"
          >
            Отмена
          </button>
          <button
            onClick={handlePay}
            disabled={!selectedMethod || loading}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-semibold py-3 rounded-xl transition-colors"
          >
            {loading ? 'Обработка...' : 'Принять оплату'}
          </button>
        </div>
      </div>
    </div>
  )
}
```

---

## Task 24: Kitchen display page

**Files:** Create `src/pages/KitchenPage.tsx`

- [ ] **Step 1: Create src/pages/KitchenPage.tsx**

```tsx
// frontend/src/pages/KitchenPage.tsx
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getOrders, updateOrderStatus } from '../api/orders'
import StatusBadge from '../components/StatusBadge'
import type { Order } from '../types'

const KITCHEN_STATUSES = ['created', 'in_progress', 'ready'] as const

export default function KitchenPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const load = async () => {
    try {
      const [created, inProgress, ready] = await Promise.all([
        getOrders('created'),
        getOrders('in_progress'),
        getOrders('ready'),
      ])
      setOrders([...created, ...inProgress, ...ready])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, 15000)
    return () => clearInterval(interval)
  }, [])

  const advance = async (order: Order) => {
    const next: Record<string, Order['status']> = {
      created: 'in_progress',
      in_progress: 'ready',
      ready: 'delivered',
    }
    const nextStatus = next[order.status]
    if (!nextStatus) return
    await updateOrderStatus(order.id, nextStatus)
    load()
  }

  const COLUMN_TITLE: Record<string, string> = {
    created: 'Новые',
    in_progress: 'Готовятся',
    ready: 'Готовы к выдаче',
  }

  const COLUMN_COLOR: Record<string, string> = {
    created: 'bg-blue-50 border-blue-200',
    in_progress: 'bg-orange-50 border-orange-200',
    ready: 'bg-green-50 border-green-200',
  }

  const BUTTON_COLOR: Record<string, string> = {
    created: 'bg-orange-500 hover:bg-orange-600',
    in_progress: 'bg-green-600 hover:bg-green-700',
    ready: 'bg-gray-600 hover:bg-gray-700',
  }

  const BUTTON_LABEL: Record<string, string> = {
    created: 'В работу',
    in_progress: 'Готово',
    ready: 'Выдано',
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="px-6 py-4 bg-gray-800 flex items-center justify-between">
        <h1 className="text-xl font-bold">Кухня — TableFlow</h1>
        <div className="flex gap-4">
          <button onClick={load} className="text-sm text-gray-400 hover:text-white">
            Обновить
          </button>
          <button onClick={() => navigate('/')} className="text-sm text-gray-400 hover:text-white">
            ← Назад
          </button>
        </div>
      </header>

      {loading ? (
        <p className="text-center text-gray-400 py-12">Загрузка...</p>
      ) : (
        <div className="grid grid-cols-3 gap-4 p-4">
          {KITCHEN_STATUSES.map((col) => {
            const colOrders = orders.filter((o) => o.status === col)
            return (
              <div key={col}>
                <h2 className="text-lg font-semibold mb-3 text-gray-300">
                  {COLUMN_TITLE[col]}
                  <span className="ml-2 bg-gray-700 text-white text-xs px-2 py-0.5 rounded-full">
                    {colOrders.length}
                  </span>
                </h2>
                <div className="space-y-3">
                  {colOrders.length === 0 && (
                    <p className="text-gray-500 text-sm text-center py-4">Пусто</p>
                  )}
                  {colOrders.map((order) => (
                    <div
                      key={order.id}
                      className={`rounded-xl border p-4 ${COLUMN_COLOR[col]}`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-gray-800">
                          {order.table_number ? `Стол #${order.table_number}` : 'Без стола'}
                        </span>
                        <span className="text-xs text-gray-500">
                          #{order.id}
                        </span>
                      </div>
                      <ul className="space-y-1 mb-3">
                        {order.items.map((item) => (
                          <li key={item.id} className="text-sm text-gray-700 flex justify-between">
                            <span>{item.product.name}</span>
                            <span className="font-medium">×{item.quantity}</span>
                          </li>
                        ))}
                      </ul>
                      {order.comment && (
                        <p className="text-xs text-gray-500 italic mb-2">{order.comment}</p>
                      )}
                      <button
                        onClick={() => advance(order)}
                        className={`w-full text-white text-sm font-medium py-2 rounded-lg transition-colors ${BUTTON_COLOR[col]}`}
                      >
                        {BUTTON_LABEL[col]}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
```

---

## Self-Review Checklist

- [x] **Spec coverage:** All main POS flows covered — auth, table selection, order creation, menu browsing, adding/removing items, payment, kitchen display.
- [x] **Placeholder scan:** No TBDs. All code is complete.
- [x] **Type consistency:** `Order`, `Product`, `Table`, etc. types defined once in `types/index.ts` and used throughout.
- [x] **Import paths:** All Django apps use `apps.<name>` consistently after Task 2/3.
- [x] **Missing `__init__.py`:** restaurants, tables — Task 4/5 create them.
- [x] **ForeignKey string refs in Order model** (`'tables.Table'`, `'restaurants.Restaurant'`, etc.) — these use app_label which defaults to last part of dotted name, so they are fine with `apps.tables` registered.
- [x] **Payment view** uses `order_id` / `method_id` from request.data — matches `createPayment` in frontend.
- [x] **`remove_item` URL pattern** — uses `url_path='remove_item/(?P<item_id>[^/.]+)'` which Django REST router supports via `@action`.

---

**Plan complete. Two execution options:**

**1. Subagent-Driven (recommended)** — Fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute all tasks in this session using executing-plans.

Which approach?
