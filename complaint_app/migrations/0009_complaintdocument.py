# Generated by Django 4.1.7 on 2023-03-15 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('complaint_app', '0008_alter_complaintmodel_complaint_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComplaintDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, upload_to='')),
                ('complaint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='complaint_app.complaintmodel')),
            ],
        ),
    ]
