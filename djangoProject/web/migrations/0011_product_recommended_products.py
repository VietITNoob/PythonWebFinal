# Generated by Django 5.1.3 on 2024-12-22 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0010_alter_developer_id_alter_developer_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='recommended_products',
            field=models.ManyToManyField(blank=True, to='web.product'),
        ),
    ]