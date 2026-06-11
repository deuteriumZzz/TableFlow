import pytest


@pytest.mark.django_db
class TestMenuScoping:
    def test_products_scoped_to_restaurant(self, waiter_client, product, restaurant_b):
        from apps.menu.models import Product, Category
        cat_b = Category.objects.create(name='B Cat', restaurant=restaurant_b, is_active=True)
        Product.objects.create(
            name='Other dish', price='50.00',
            restaurant=restaurant_b, category=cat_b, is_active=True,
        )
        resp = waiter_client.get('/api/menu/products/')
        names = [p['name'] for p in resp.json()['results']]
        assert product.name in names
        assert 'Other dish' not in names

    def test_inactive_products_excluded(self, waiter_client, restaurant, category):
        from apps.menu.models import Product
        Product.objects.create(
            name='Hidden', price='99.00',
            restaurant=restaurant, category=category, is_active=False,
        )
        resp = waiter_client.get('/api/menu/products/')
        names = [p['name'] for p in resp.json()['results']]
        assert 'Hidden' not in names

    def test_filter_by_category(self, waiter_client, product, restaurant, category):
        from apps.menu.models import Product, Category
        cat2 = Category.objects.create(name='Cat 2', restaurant=restaurant, is_active=True)
        Product.objects.create(
            name='Cat2 dish', price='30.00',
            restaurant=restaurant, category=cat2, is_active=True,
        )
        resp = waiter_client.get(f'/api/menu/products/?category={category.id}')
        names = [p['name'] for p in resp.json()['results']]
        assert product.name in names
        assert 'Cat2 dish' not in names


@pytest.mark.django_db
class TestMenuPermissions:
    def test_waiter_cannot_create_product(self, waiter_client, category, restaurant):
        resp = waiter_client.post('/api/menu/products/', {
            'name': 'New', 'price': '100.00',
            'category': category.id, 'restaurant': restaurant.id,
        })
        assert resp.status_code == 403

    def test_manager_can_create_product(self, manager_client, category, restaurant):
        resp = manager_client.post('/api/menu/products/', {
            'name': 'Manager dish', 'price': '100.00',
            'category_id': category.id,
        })
        assert resp.status_code == 201
