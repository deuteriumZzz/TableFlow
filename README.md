# TableFlow

POS-система для ресторанов с кухонной доской в реальном времени, бронированием столов и отчётностью.

## Содержание

- [Возможности](#возможности)
- [Стек технологий](#стек-технологий)
- [Быстрый старт (Docker)](#быстрый-старт-docker)
- [Локальная разработка](#локальная-разработка)
- [Переменные окружения](#переменные-окружения)
- [API документация](#api-документация)
- [Запуск тестов](#запуск-тестов)
- [Деплой в Kubernetes](#деплой-в-kubernetes)
- [Структура проекта](#структура-проекта)
- [Роли пользователей](#роли-пользователей)

---

## Возможности

| Модуль | Что умеет |
|---|---|
| **POS-касса** | Выбор стола → создание заказа → добавление блюд с модификаторами → оплата |
| **Кухонная доска** | Трёхколоночный канбан (Новые / Готовятся / Готовы); обновления через WebSocket без перезагрузки |
| **Бронирование** | Создание, подтверждение, отмена брони; фильтрация по дате |
| **Меню** | Категории, блюда, модификаторы; управление остатками |
| **Персонал** | Расписания и зарплаты сотрудников |
| **Отчёты** | Выручка за день, продажи по блюду с кешированием в БД |
| **Мультиресторанность** | Данные каждого ресторана полностью изолированы |

---

## Стек технологий

**Backend**
- Python 3.11 · Django 4.2 · Django REST Framework 3.14
- Django Channels 4.2 + Daphne (WebSocket / ASGI)
- PostgreSQL · JWT-аутентификация (simplejwt)
- drf-spectacular (OpenAPI / Swagger)

**Frontend**
- React 18 · TypeScript · Vite
- Zustand (state management)
- Tailwind CSS
- Axios · React Router 6

**Инфраструктура**
- Docker · Docker Compose
- Kubernetes (манифесты в `k8s/`)
- GitHub Actions (lint / test / build)

---

## Быстрый старт (Docker)

```bash
git clone <repo-url>
cd TableFlow

cp .env.example .env          # при необходимости отредактируйте пароли

docker compose up --build
```

| Сервис | URL |
|---|---|
| Frontend | http://localhost |
| Backend API | http://localhost:8000/api/ |
| Swagger UI | http://localhost:8000/api/docs/ |

### Создание первого ресторана и администратора

```bash
docker compose exec backend python manage.py shell -c "
from apps.restaurants.models import Restaurant
from apps.accounts.models import User
from apps.tables.models import Table
from apps.payments.models import PaymentMethod

r = Restaurant.objects.create(name='Мой ресторан', currency='RUB')
User.objects.create_superuser('admin', 'admin@example.com', 'changeme', role='admin', restaurant=r)
for i in range(1, 11):
    Table.objects.create(restaurant=r, number=i, capacity=4)
PaymentMethod.objects.create(name='Наличные')
PaymentMethod.objects.create(name='Банковская карта')
print('OK')
"
```

---

## Локальная разработка

### Требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (или запустить только БД через Docker)

### Backend

```bash
cd backend

python -m venv ../venv
source ../venv/bin/activate          # Windows: ..\venv\Scripts\activate

pip install -r requirements.txt

cp ../.env.example ../.env
# Укажите DATABASE_URL в .env, например:
# DATABASE_URL=postgresql://tableflow:tableflow_dev_password@localhost:5432/tableflow

python manage.py migrate
python manage.py runserver
```

Либо запустить только PostgreSQL через Docker и подключиться к нему:

```bash
docker compose up postgres -d
```

### Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:3000
```

Vite автоматически проксирует `/api` и `/media` на `http://localhost:8000`.

---

## Переменные окружения

Скопируйте `.env.example` в `.env` и заполните значения.

| Переменная | По умолчанию | Описание |
|---|---|---|
| `SECRET_KEY` | *(insecure default)* | Django secret key — **обязательно сменить в prod** |
| `DEBUG` | `True` | Режим отладки |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Разрешённые хосты через запятую |
| `DATABASE_URL` | SQLite | URL подключения к БД |
| `CORS_ALLOW_ALL_ORIGINS` | `False` | Разрешить CORS для всех источников |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,...` | Список разрешённых origins |
| `REDIS_URL` | *(пусто)* | URL Redis для WebSocket channel layer в prod (без него — in-memory) |
| `DJANGO_LOG_LEVEL` | `INFO` | Уровень логирования Django |
| `POSTGRES_DB/USER/PASSWORD` | `tableflow` | Параметры PostgreSQL для docker-compose |

---

## API документация

После запуска сервера документация доступна по адресам:

- **Swagger UI** — `http://localhost:8000/api/docs/`
- **OpenAPI схема** — `http://localhost:8000/api/schema/`

### Основные эндпоинты

| Метод | URL | Описание |
|---|---|---|
| `POST` | `/api/token/` | Получить JWT-токен |
| `POST` | `/api/token/refresh/` | Обновить токен |
| `GET` | `/api/orders/` | Список заказов ресторана |
| `POST` | `/api/orders/{id}/add_item/` | Добавить позицию в заказ |
| `DELETE` | `/api/orders/{id}/remove_item/{item_id}/` | Удалить позицию |
| `POST` | `/api/orders/{id}/update_status/` | Сменить статус заказа |
| `POST` | `/api/orders/{id}/item_status/{item_id}/` | Сменить статус позиции |
| `POST` | `/api/payments/` | Принять оплату |
| `GET` | `/api/menu/products/` | Каталог блюд |
| `GET` | `/api/tables/` | Список столов |
| `GET` | `/api/reservations/` | Бронирования |
| `POST` | `/api/reservations/{id}/confirm/` | Подтвердить бронь |
| `POST` | `/api/reservations/{id}/cancel/` | Отменить бронь |
| `GET` | `/api/reports/sales/` | Отчёт по выручке |
| `GET` | `/api/health/` | Health check |

### WebSocket

```
ws://localhost:8000/ws/orders/{restaurant_id}/
```

Сервер отправляет событие при любом изменении статуса заказа:

```json
{ "type": "order_update", "order_id": 42, "status": "in_progress" }
```

---

## Запуск тестов

```bash
cd backend
source ../venv/bin/activate

# Все тесты с покрытием
pytest --cov=apps --cov-report=term-missing

# Конкретный модуль
pytest apps/orders/tests.py -v
```

Тесты используют SQLite in-memory и не требуют запущенного PostgreSQL.

---

## Деплой в Kubernetes

Подробная инструкция в [k8s/README.md](k8s/README.md).

Краткий сценарий:

```bash
# 1. Собрать и запушить образы
REGISTRY=your-registry.io/tableflow
docker build -t $REGISTRY/backend:latest ./backend && docker push $REGISTRY/backend:latest
docker build -t $REGISTRY/frontend:latest ./frontend && docker push $REGISTRY/frontend:latest

# 2. Обновить image: в k8s/backend/deployment.yaml и k8s/frontend/deployment.yaml

# 3. Применить манифесты
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/ingress.yaml
```

> Для работы WebSocket в prod необходим Redis. Укажите `REDIS_URL` в `k8s/backend/secret.yaml`.

---

## Структура проекта

```
TableFlow/
├── backend/
│   ├── apps/
│   │   ├── accounts/       # Пользователи и аутентификация
│   │   ├── api/            # Общие утилиты: permissions, pagination, filters, health
│   │   ├── menu/           # Категории, блюда, модификаторы
│   │   ├── orders/         # Заказы, позиции, WebSocket consumer
│   │   ├── payments/       # Оплата, методы оплаты
│   │   ├── reports/        # Отчёты по выручке и блюдам
│   │   ├── reservations/   # Бронирование столов
│   │   ├── restaurants/    # Рестораны
│   │   ├── staff/          # Расписания и зарплаты
│   │   └── tables/         # Столы
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── routing.py      # ASGI + WebSocket routing
│   ├── entrypoint.sh       # migrate → collectstatic → daphne
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/            # Axios-клиенты для каждого домена
│   │   ├── components/     # TableGrid, MenuPanel, OrderPanel, PaymentModal…
│   │   ├── pages/          # TablesPage, POSPage, KitchenPage, ReservationPage…
│   │   ├── store/          # Zustand: authStore, posStore
│   │   └── types/          # TypeScript-интерфейсы
│   └── Dockerfile
├── k8s/                    # Kubernetes манифесты
├── .env.example
└── docker-compose.yml
```

---

## Роли пользователей

| Роль | Доступ |
|---|---|
| `admin` | Полный доступ ко всем данным ресторана |
| `manager` | Управление меню, персоналом, отчёты |
| `cashier` | Заказы, оплата, меню (чтение) |
| `waiter` | Создание заказов, добавление блюд |
| `chef` | Кухонная доска (смена статусов) |
| `auditor` | Только чтение отчётов |

Все данные строго изолированы по ресторану — пользователь видит только данные своего заведения.
