import pytest
from apps.orders.models import Order


@pytest.mark.django_db
class TestPayment:
    ORDERS_URL = '/api/orders/'
    PAYMENTS_URL = '/api/payments/'

    def _create_order(self, client, table):
        resp = client.post(self.ORDERS_URL, {'table': table.id})
        return resp.data['id']

    def test_create_payment_marks_order_paid(self, admin_client, table, payment_method):
        order_id = self._create_order(admin_client, table)
        resp = admin_client.post(self.PAYMENTS_URL, {
            'order_id': order_id,
            'method_id': payment_method.id,
        })
        assert resp.status_code == 201
        assert resp.data['status'] == 'success'
        order = Order.objects.get(id=order_id)
        assert order.payment_status == 'paid'
        assert order.status == 'delivered'

    def test_create_payment_frees_table(self, admin_client, table, payment_method):
        order_id = self._create_order(admin_client, table)
        admin_client.post(self.PAYMENTS_URL, {
            'order_id': order_id,
            'method_id': payment_method.id,
        })
        table.refresh_from_db()
        assert table.status == 'free'

    def test_double_payment_fails(self, admin_client, table, payment_method):
        order_id = self._create_order(admin_client, table)
        admin_client.post(self.PAYMENTS_URL, {'order_id': order_id, 'method_id': payment_method.id})
        resp2 = admin_client.post(self.PAYMENTS_URL, {'order_id': order_id, 'method_id': payment_method.id})
        assert resp2.status_code == 400

    def test_payment_for_nonexistent_order(self, admin_client, payment_method):
        resp = admin_client.post(self.PAYMENTS_URL, {
            'order_id': 99999,
            'method_id': payment_method.id,
        })
        assert resp.status_code == 404

    def test_payment_requires_auth(self, api_client, table, payment_method):
        resp = api_client.post(self.PAYMENTS_URL, {'order_id': 1, 'method_id': payment_method.id})
        assert resp.status_code == 401
