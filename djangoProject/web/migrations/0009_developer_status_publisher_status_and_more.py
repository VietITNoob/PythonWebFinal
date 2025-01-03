# Generated by Django 5.1.3 on 2024-12-22 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0008_remove_developer_status_remove_publisher_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='developer',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=8),
        ),
        migrations.AddField(
            model_name='publisher',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=8),
        ),
        migrations.AlterField(
            model_name='developer',
            name='name',
            field=models.CharField(blank=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='name',
            field=models.CharField(blank=True, max_length=255, unique=True),
        ),
    ]
