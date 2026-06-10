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
        self.stdout.write('  Tables: 1-10 created')

        cat_main, _ = Category.objects.get_or_create(
            name='Основные блюда',
            restaurant=restaurant,
            defaults={'sort_order': 1, 'is_active': True},
        )
        cat_drinks, _ = Category.objects.get_or_create(
            name='Напитки',
            restaurant=restaurant,
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
