# Generated by Django 5.2.1 on 2025-07-06 11:37

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_customer_email_alter_product_store_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Store',
            new_name='Shop',
        ),
    ]
