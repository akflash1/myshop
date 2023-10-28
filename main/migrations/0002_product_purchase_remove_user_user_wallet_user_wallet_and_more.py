# Generated by Django 4.2.6 on 2023-10-24 18:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantiti', models.PositiveIntegerField()),
                ('purchase_time', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_products', to='main.product')),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_wallet',
        ),
        migrations.AddField(
            model_name='user',
            name='wallet',
            field=models.DecimalField(decimal_places=2, default=10000, max_digits=10),
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refund_time', models.DateTimeField(auto_now_add=True)),
                ('refund_purchase', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.purchase')),
            ],
        ),
        migrations.AddField(
            model_name='purchase',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_purchases', to=settings.AUTH_USER_MODEL),
        ),
    ]
