from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
        ('restaurants', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesreport',
            name='restaurant',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='restaurants.restaurant',
            ),
        ),
        migrations.AddField(
            model_name='productreport',
            name='restaurant',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='restaurants.restaurant',
            ),
        ),
        migrations.AlterField(
            model_name='salesreport',
            name='generated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name='salesreport',
            unique_together={('restaurant', 'date')},
        ),
        migrations.AlterUniqueTogether(
            name='productreport',
            unique_together={('restaurant', 'product', 'date')},
        ),
    ]
