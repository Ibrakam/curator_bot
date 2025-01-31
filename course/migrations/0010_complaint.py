# Generated by Django 5.1.4 on 2024-12-18 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0009_user_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('complain', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Жалоба',
                'verbose_name_plural': 'Жалобы',
                'db_table': 'complaints',
            },
        ),
    ]
