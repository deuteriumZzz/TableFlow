import pytest
from decimal import Decimal
from apps.orders.models import Order, OrderItem


@pytest.mark.django_db
class TestOrderCreate:
    def test_create_order(self, waiter_client, table):
        resp = waiter_client.post('/api/orders/', {'table': table.id})
        assert resp.status_code == 201
        assert resp.json()['status'] == 'created'
        assert resp.json()['payment_status'] == 'pending'

    def test_create_order_marks_table_occupied(self, waiter_client, table):
        waiter_client.post('/api/orders/', {'table': table.id})
        table.refresh_from_db()
        assert table.status == 'occupied'

    def test_create_order_requires_auth(self, api_client, table):
        resp = api_client.post('/api/orders/', {'table': table.id})
        assert resp.status_code == 401

    def test_create_order_sets_restaurant(self, waiter_client, waiter_user, table):
        resp = waiter_client.post('/api/orders/', {'table': table.id})
        order = Order.objects.get(id=resp.json()['id'])
        assert order.restaurant == waiter_user.restaurant

    def test_list_scoped_to_restaurant(self, waiter_client, restaurant_b, table_b):
        from apps.accounts.models import User
        from rest_framework.test import APIClient
        user_b = User.objects.create_user(
            username='waiter_b2', password='pass', role='waiter', restaurant=restaurant_b,
        )
        client_b = APIClient()
        client_b.force_authenticate(user=user_b)
        client_b.post('/api/orders/', {'table': table_b.id})
        resp = waiter_client.get('/api/orders/')
        order_ids = {o['id'] for o in resp.json()['results']}
        b_order_ids = set(Order.objects.filter(restaurant=restaurant_b).values_list('id', flat=True))
        assert order_ids.isdisjoint(b_order_ids)


@pytest.mark.django_db
class TestAddItem:
    def _create_order(self, client, table):
        return client.post('/api/orders/', {'table': table.id}).json()['id']

    def test_add_item_increases_total(self, waiter_client, table, product):
        order_id = self._create_order(waiter_client, table)
        resp = waiter_client.post(f'/api/orders/{order_id}/add_item/', {
            'product_id': product.id, 'quantity': 2,
        })
        assert resp.status_code == 200
        assert Decimal(resp.json()['total_amount']) == Decimal(product.price) * 2

    def test_add_item_out_of_stock_rejected(self, waiter_client, table, product):
        product.status = 'out_of_stock'
        product.save()
        order_id = self._create_order(waiter_client, table)
        resp = waiter_client.post(f'/api/orders/{order_id}/add_item/', {
            'product_id': product.id, 'quantity': 1,
        })
        assert resp.status_code == 400

    def test_add_item_decrements_stock(self, waiter_client, table, product):
        product.current_stock = 10
        product.save()
        order_id = self._create_order(waiter_client, table)
        waiter_client.post(f'/api/orders/{order_id}/add_item/', {
            'product_id': product.id, 'quantity': 3,
        })
        product.refresh_from_db()
        assert product.current_stock == 7

    def test_add_item_to_delivered_order_rejected(self, waiter_client, table, product):
        order_id = self._create_order(waiter_client, table)
        Order.objects.filter(pk=order_id).update(status='delivered')
        resp = waiter_client.post(f'/api/orders/{order_id}/add_item/', {
            'product_id': product.id, 'quantity': 1,
        })
        assert resp.status_code == 400

    def test_add_item_wrong_restaurant_product_rejected(self, waiter_client, table, restaurant_b):
        from apps.menu.models import Category, Product
        cat = Category.objects.create(name='Other', restaurant=restaurant_b, sort_order=1)
        other_product = Product.objects.create(
            name='Чужое блюдо', price='50.00',
            restaurant=restaurant_b, category=cat, is_active=True, status='available',
        )
        order_id = self._create_order(waiter_client, table)
        resp = waiter_client.post(f'/api/orders/{order_id}/add_item/', {
            'product_id': other_product.id, 'quantity': 1,
        })
        assert resp.status_code == 404


@pytest.mark.django_db
class TestRemoveItem:
    def test_remove_item_recalculates_total(self, waiter_client, table, product):
        order_id = waiter_client.post('/api/orders/', {'table': table.id}).json()['id']
        add = waiter_client.post(f'/api/orders/{order_id}/add_item/', {
            'product_id': product.id, 'quantity': 2,
        })
        item_id = add.json()['items'][0]['id']
        resp = waiter_client.delete(f'/api/orders/{order_id}/remove_item/{item_id}/')
        assert resp.status_code == 200
        assert Decimal(resp.json()['total_amount']) == 0


@pytest.mark.django_db
class TestUpdateStatus:
    def test_update_order_status(self, waiter_client, table):
        order_id = waiter_client.post('/api/orders/', {'table': table.id}).json()['id']
        resp = waiter_client.post(f'/api/orders/{order_id}/update_status/', {'status': 'in_progress'})
        assert resp.status_code == 200
        assert resp.json()['status'] == 'in_progress'

    def test_delivered_frees_table(self, waiter_client, table):
        order_id = waiter_client.post('/api/orders/', {'table': table.id}).json()['id']
        waiter_client.post(f'/api/orders/{order_id}/update_status/', {'status': 'delivered'})
        table.refresh_from_db()
        assert table.status == 'free'

    def test_invalid_status_rejected(self, waiter_client, table):
        order_id = waiter_client.post('/api/orders/', {'table': table.id}).json()['id']
        resp = waiter_client.post(f'/api/orders/{order_id}/update_status/', {'status': 'flying'})
        assert resp.status_code == 400


@pytest.mark.django_db
class TestUpdateItemStatus:
    def test_update_item_status(self, waiter_client, table, product):
        order_id = waiter_client.post('/api/orders/', {'table': table.id}).json()['id']
        add = waiter_client.post(f'/api/orders/{order_id}/add_item/', {
            'product_id': product.id, 'quantity': 1,
        })
        item_id = add.json()['items'][0]['id']
        resp = waiter_client.post(f'/api/orders/{order_id}/item_status/{item_id}/', {'status': 'ready'})
        assert resp.status_code == 200
        item = next(i for i in resp.json()['items'] if i['id'] == item_id)
        assert item['status'] == 'ready'


@pytest.mark.django_db
class TestRecalculateTotal:
    def test_discount_applied(self, restaurant, table, product, waiter_user):
        order = Order.objects.create(
            restaurant=restaurant, table=table, waitress=waiter_user,
            discount=Decimal('20.00'), tax=Decimal('0'),
        )
        OrderItem.objects.create(
            order=order, product=product,
            quantity=1, price=product.price, total_price=product.price,
        )
        order.recalculate_total()
        assert order.total_amount == Decimal(product.price) - Decimal('20.00')

    def test_tax_applied(self, restaurant, table, product, waiter_user):
        order = Order.objects.create(
            restaurant=restaurant, table=table, waitress=waiter_user,
            discount=Decimal('0'), tax=Decimal('10.00'),
        )
        OrderItem.objects.create(
            order=order, product=product,
            quantity=1, price=product.price, total_price=product.price,
        )
        order.recalculate_total()
        assert order.total_amount == Decimal(product.price) + Decimal('10.00')
