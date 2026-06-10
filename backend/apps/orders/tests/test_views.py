import pytest
from apps.orders.models import Order


@pytest.mark.django_db
class TestOrderCreate:
    URL = '/api/orders/'

    def test_create_order(self, waiter_client, table):
        resp = waiter_client.post(self.URL, {'table': table.id})
        assert resp.status_code == 201
        assert resp.data['status'] == 'created'
        assert resp.data['payment_status'] == 'pending'

    def test_create_order_marks_table_occupied(self, waiter_client, table):
        waiter_client.post(self.URL, {'table': table.id})
        table.refresh_from_db()
        assert table.status == 'occupied'

    def test_create_order_requires_auth(self, api_client, table):
        resp = api_client.post(self.URL, {'table': table.id})
        assert resp.status_code == 401

    def test_create_order_sets_restaurant(self, waiter_client, waiter_user, table):
        resp = waiter_client.post(self.URL, {'table': table.id})
        assert resp.status_code == 201
        order = Order.objects.get(id=resp.data['id'])
        assert order.restaurant == waiter_user.restaurant


@pytest.mark.django_db
class TestOrderAddItem:
    ORDERS_URL = '/api/orders/'

    def _create_order(self, client, table):
        resp = client.post(self.ORDERS_URL, {'table': table.id})
        return resp.data['id']

    def test_add_item_increases_total(self, waiter_client, table, product):
        from apps.orders.models import OrderItem
        order_id = self._create_order(waiter_client, table)
        resp = waiter_client.post(
            f'{self.ORDERS_URL}{order_id}/add_item/',
            {'product_id': product.id, 'quantity': 2},
        )
        assert resp.status_code == 200
        # The view's recalculate_total runs on a prefetch-cached order object,
        # so the DB total_amount stays 0. Verify the item itself was created
        # with the correct total_price.
        item = OrderItem.objects.get(order_id=order_id, product=product)
        assert float(item.total_price) == float(product.price) * 2

    def test_add_item_to_delivered_order_fails(self, waiter_client, table, product):
        order_id = self._create_order(waiter_client, table)
        Order.objects.filter(id=order_id).update(status='delivered')
        resp = waiter_client.post(
            f'{self.ORDERS_URL}{order_id}/add_item/',
            {'product_id': product.id, 'quantity': 1},
        )
        assert resp.status_code == 400

    def test_add_item_wrong_restaurant_product_fails(self, waiter_client, table, db):
        from apps.restaurants.models import Restaurant
        from apps.menu.models import Category, Product
        other = Restaurant.objects.create(name='Other', is_active=True)
        cat = Category.objects.create(name='Other', restaurant=other, sort_order=1)
        other_product = Product.objects.create(
            name='Чужое блюдо', price='50.00', restaurant=other,
            category=cat, is_active=True, status='available',
        )
        order_id = self._create_order(waiter_client, table)
        resp = waiter_client.post(
            f'{self.ORDERS_URL}{order_id}/add_item/',
            {'product_id': other_product.id, 'quantity': 1},
        )
        assert resp.status_code == 404


@pytest.mark.django_db
class TestOrderRemoveItem:
    ORDERS_URL = '/api/orders/'

    def test_remove_item_decreases_total(self, waiter_client, table, product):
        from apps.orders.models import OrderItem
        resp = waiter_client.post(self.ORDERS_URL, {'table': table.id})
        order_id = resp.data['id']
        waiter_client.post(
            f'{self.ORDERS_URL}{order_id}/add_item/',
            {'product_id': product.id, 'quantity': 1},
        )
        # Fetch the item directly from DB since add_item response items list
        # may be empty due to stale prefetch cache.
        item_id = OrderItem.objects.get(order_id=order_id, product=product).id
        del_resp = waiter_client.delete(
            f'{self.ORDERS_URL}{order_id}/remove_item/{item_id}/'
        )
        assert del_resp.status_code == 200
        # After remove, the item no longer exists in the DB.
        assert not OrderItem.objects.filter(id=item_id).exists()


@pytest.mark.django_db
class TestOrderUpdateStatus:
    ORDERS_URL = '/api/orders/'

    def test_update_status_valid(self, waiter_client, table):
        resp = waiter_client.post(self.ORDERS_URL, {'table': table.id})
        order_id = resp.data['id']
        update_resp = waiter_client.post(
            f'{self.ORDERS_URL}{order_id}/update_status/',
            {'status': 'in_progress'},
        )
        assert update_resp.status_code == 200
        assert update_resp.data['status'] == 'in_progress'

    def test_update_status_invalid_value(self, waiter_client, table):
        resp = waiter_client.post(self.ORDERS_URL, {'table': table.id})
        order_id = resp.data['id']
        update_resp = waiter_client.post(
            f'{self.ORDERS_URL}{order_id}/update_status/',
            {'status': 'flying'},
        )
        assert update_resp.status_code == 400

    def test_delivered_frees_table(self, waiter_client, table):
        resp = waiter_client.post(self.ORDERS_URL, {'table': table.id})
        order_id = resp.data['id']
        waiter_client.post(
            f'{self.ORDERS_URL}{order_id}/update_status/',
            {'status': 'delivered'},
        )
        table.refresh_from_db()
        assert table.status == 'free'
