import pytest
from django.utils import timezone
from datetime import timedelta

from apps.reservations.models import Reservation


@pytest.fixture
def future_dt():
    return timezone.now() + timedelta(hours=2)


@pytest.fixture
def reservation(db, restaurant, table, waiter_user, future_dt):
    return Reservation.objects.create(
        restaurant=restaurant,
        table=table,
        guest_name='Иван Иванов',
        guest_phone='+79001234567',
        guest_count=2,
        reserved_at=future_dt,
        created_by=waiter_user,
    )


@pytest.mark.django_db
class TestReservationCRUD:
    def test_create_reservation(self, waiter_client, table, future_dt):
        resp = waiter_client.post('/api/reservations/', {
            'table': table.id,
            'guest_name': 'Пётр Петров',
            'guest_phone': '+79009876543',
            'guest_count': 3,
            'reserved_at': future_dt.isoformat(),
        })
        assert resp.status_code == 201
        assert resp.json()['status'] == 'pending'

    def test_list_scoped_to_restaurant(self, waiter_client, reservation, restaurant_b, table_b, future_dt):
        from apps.accounts.models import User
        from rest_framework.test import APIClient
        user_b = User.objects.create_user(
            username='waiter_b', password='pass', role='waiter', restaurant=restaurant_b,
        )
        Reservation.objects.create(
            restaurant=restaurant_b, table=table_b,
            guest_name='Другой гость', guest_phone='+70000000000',
            guest_count=1, reserved_at=future_dt, created_by=user_b,
        )
        resp = waiter_client.get('/api/reservations/')
        names = [r['guest_name'] for r in resp.json()['results']]
        assert 'Иван Иванов' in names
        assert 'Другой гость' not in names

    def test_filter_by_date(self, waiter_client, reservation, future_dt):
        date_str = future_dt.date().isoformat()
        resp = waiter_client.get(f'/api/reservations/?date={date_str}')
        assert resp.status_code == 200
        assert len(resp.json()['results']) >= 1


@pytest.mark.django_db
class TestReservationActions:
    def test_confirm_sets_table_reserved(self, waiter_client, reservation, table):
        resp = waiter_client.post(f'/api/reservations/{reservation.id}/confirm/')
        assert resp.status_code == 200
        assert resp.json()['status'] == 'confirmed'
        table.refresh_from_db()
        assert table.status == 'reserved'

    def test_confirm_only_from_pending(self, waiter_client, reservation):
        reservation.status = 'confirmed'
        reservation.save()
        resp = waiter_client.post(f'/api/reservations/{reservation.id}/confirm/')
        assert resp.status_code == 400

    def test_cancel_frees_table(self, waiter_client, reservation, table):
        waiter_client.post(f'/api/reservations/{reservation.id}/confirm/')
        resp = waiter_client.post(f'/api/reservations/{reservation.id}/cancel/')
        assert resp.status_code == 200
        assert resp.json()['status'] == 'cancelled'
        table.refresh_from_db()
        assert table.status == 'free'

    def test_cancel_already_cancelled_rejected(self, waiter_client, reservation):
        reservation.status = 'cancelled'
        reservation.save()
        resp = waiter_client.post(f'/api/reservations/{reservation.id}/cancel/')
        assert resp.status_code == 400
