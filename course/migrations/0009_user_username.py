# Generated by Django 5.1.4 on 2024-12-15 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0008_answerforcomplain_delete_course_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]