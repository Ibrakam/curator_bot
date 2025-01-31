# Generated by Django 5.1.4 on 2024-12-12 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContactInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=20)),
                ('tg_username', models.CharField(max_length=100)),
                ('role', models.CharField(choices=[('sales_department', 'Отдел продаж'), ('curator', 'Куратор'), ('support', 'Поддержка')], default='sales_department', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.FloatField()),
                ('start_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('name', models.CharField(max_length=100)),
                ('surname', models.CharField(max_length=100)),
                ('course', models.CharField(max_length=100)),
                ('stream', models.CharField(max_length=100)),
                ('reason', models.TextField()),
                ('status', models.CharField(default='pending', max_length=100)),
                ('admin_notes', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='RequestModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('department', models.CharField(max_length=100)),
                ('request_type', models.CharField(max_length=100)),
                ('status', models.CharField(default='pending', max_length=100)),
                ('details', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(unique=True)),
                ('phone', models.CharField(max_length=20)),
                ('full_name', models.CharField(max_length=100)),
                ('role', models.CharField(choices=[('admin', 'admin'), ('user', 'user'), ('sales_department', 'Отдел продаж'), ('curator', 'Куратор'), ('support', 'Поддержка'), ('refund', 'Возврат')], default='user', max_length=100)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
