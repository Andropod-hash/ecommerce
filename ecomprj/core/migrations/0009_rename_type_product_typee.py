# Generated by Django 4.2.1 on 2023-12-04 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_product_life_product_mfd_product_stock_count_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='type',
            new_name='typee',
        ),
    ]
