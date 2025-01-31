# Generated by Django 5.1.4 on 2024-12-15 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0007_alter_refund_status_alter_user_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerForComplain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('answer', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Ответ на жалобу',
                'verbose_name_plural': 'Ответы на жалобы',
                'db_table': 'answers_for_complain',
            },
        ),
        migrations.DeleteModel(
            name='Course',
        ),
        migrations.AlterField(
            model_name='refund',
            name='admin_notes',
            field=models.FileField(blank=True, null=True, upload_to='call_records'),
        ),
    ]
