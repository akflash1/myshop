# Generated by Django 4.2.6 on 2023-10-24 18:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_product_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchase',
            old_name='quantiti',
            new_name='quantity',
        ),
    ]
