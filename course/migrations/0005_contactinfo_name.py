# Generated by Django 5.1.4 on 2024-12-13 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_alter_requestmodel_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactinfo',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
