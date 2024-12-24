# Generated by Django 5.1.4 on 2024-12-19 13:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0011_complaint_user_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='user_info',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='course.user', to_field='phone'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]