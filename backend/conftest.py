import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.menu.models import Category, Product
from apps.payments.models import PaymentMethod
from apps.restaurants.models import Restaurant
from apps.tables.models import Table


@pytest.fixture
def restaurant(db):
    return Restaurant.objects.create(name='Test Restaurant', is_active=True)


@pytest.fixture
def admin_user(db, restaurant):
    return User.objects.create_user(
        username='admin_test',
        password='pass123',
        role='admin',
        restaurant=restaurant,
    )


@pytest.fixture
def manager_user(db, restaurant):
    return User.objects.create_user(
        username='manager_test',
        password='pass123',
        role='manager',
        restaurant=restaurant,
    )


@pytest.fixture
def waiter_user(db, restaurant):
    return User.objects.create_user(
        username='waiter_test',
        password='pass123',
        role='waiter',
        restaurant=restaurant,
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def manager_client(api_client, manager_user):
    api_client.force_authenticate(user=manager_user)
    return api_client


@pytest.fixture
def waiter_client(api_client, waiter_user):
    api_client.force_authenticate(user=waiter_user)
    return api_client


@pytest.fixture
def table(db, restaurant):
    return Table.objects.create(
        restaurant=restaurant, number=1, capacity=4, status='free'
    )


@pytest.fixture
def category(db, restaurant):
    return Category.objects.create(
        name='Test Category', restaurant=restaurant, is_active=True, sort_order=1
    )


@pytest.fixture
def product(db, restaurant, category):
    return Product.objects.create(
        name='Test Dish',
        price='100.00',
        restaurant=restaurant,
        category=category,
        is_active=True,
        status='available',
    )


@pytest.fixture
def payment_method(db):
    return PaymentMethod.objects.create(name='Cash')
