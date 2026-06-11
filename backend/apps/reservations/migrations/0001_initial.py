from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('restaurants', '0001_initial'),
        ('tables', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guest_name', models.CharField(max_length=200, verbose_name='Имя гостя')),
                ('guest_phone', models.CharField(max_length=20, verbose_name='Телефон гостя')),
                ('guest_count', models.PositiveIntegerField(default=1, verbose_name='Количество гостей')),
                ('reserved_at', models.DateTimeField(verbose_name='Время брони')),
                ('duration_minutes', models.PositiveIntegerField(default=120, verbose_name='Длительность (мин)')),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Ожидает'),
                        ('confirmed', 'Подтверждено'),
                        ('cancelled', 'Отменено'),
                        ('completed', 'Завершено'),
                        ('no_show', 'Не пришли'),
                    ],
                    default='pending', max_length=20, verbose_name='Статус',
                )),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('created_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='accounts.user',
                    verbose_name='Создал',
                )),
                ('restaurant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='restaurants.restaurant',
                    verbose_name='Ресторан',
                )),
                ('table', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='tables.table',
                    verbose_name='Стол',
                )),
            ],
            options={
                'verbose_name': 'Бронирование',
                'verbose_name_plural': 'Бронирования',
                'ordering': ['reserved_at'],
            },
        ),
    ]
