# Generated by Django 4.1.7 on 2023-03-21 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaint_app', '0010_actionmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionmodel',
            name='action',
            field=models.TextField(max_length=1024),
        ),
    ]
