# Generated by Django 5.2.1 on 2025-07-06 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_rename_specs_spec'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='quantity',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
    ]
