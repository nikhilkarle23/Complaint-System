# Generated by Django 4.1.7 on 2023-03-10 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaint_app', '0005_complaintmodel_solved_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaintmodel',
            name='comments',
            field=models.TextField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='complaintmodel',
            name='complaint_file',
            field=models.FileField(blank=True, upload_to='complaint_file/'),
        ),
    ]
