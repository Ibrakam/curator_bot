# Generated by Django 5.1.4 on 2024-12-13 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_contactinfo_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('question', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
                'db_table': 'questions',
            },
        ),
    ]
