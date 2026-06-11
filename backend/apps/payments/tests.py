import pytest
from apps.orders.models import Order


@pytest.fixture
def open_order(waiter_user, restaurant, table):
    return Order.objects.create(
        restaurant=restaurant, table=table, waitress=waiter_user,
        total_amount='250.00',
    )


@pytest.mark.django_db
class TestCreatePayment:
    def test_creates_payment_and_closes_order(self, waiter_client, open_order, payment_method):
        resp = waiter_client.post('/api/payments/', {
            'order_id': open_order.id,
            'method_id': payment_method.id,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data['status'] == 'success'
        assert data['amount'] == '250.00'

        open_order.refresh_from_db()
        assert open_order.payment_status == 'paid'
        assert open_order.status == 'delivered'

    def test_creates_payment_frees_table(self, waiter_client, open_order, payment_method, table):
        waiter_client.post('/api/payments/', {
            'order_id': open_order.id,
            'method_id': payment_method.id,
        })
        table.refresh_from_db()
        assert table.status == 'free'

    def test_double_payment_rejected(self, waiter_client, open_order, payment_method):
        waiter_client.post('/api/payments/', {'order_id': open_order.id, 'method_id': payment_method.id})
        resp = waiter_client.post('/api/payments/', {'order_id': open_order.id, 'method_id': payment_method.id})
        assert resp.status_code == 400

    def test_payment_for_other_restaurant_order_rejected(self, manager_client, open_order, payment_method):
        from apps.restaurants.models import Restaurant
        from apps.accounts.models import User
        other_restaurant = Restaurant.objects.create(name='Other')
        other_user = User.objects.create_user(
            username='other_waiter', password='pass123',
            role='waiter', restaurant=other_restaurant,
        )
        from rest_framework.test import APIClient
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)
        resp = other_client.post('/api/payments/', {
            'order_id': open_order.id,
            'method_id': payment_method.id,
        })
        assert resp.status_code == 404
