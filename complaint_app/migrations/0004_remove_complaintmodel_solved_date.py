# Generated by Django 4.1.7 on 2023-03-09 10:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('complaint_app', '0003_alter_complaintmodel_solved_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='complaintmodel',
            name='solved_date',
        ),
    ]
