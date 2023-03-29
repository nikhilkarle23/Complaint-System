from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
import datetime

# Create your models here.
USER_TYPE = (
    ('customer', 'Customer'),
    ('agent', 'Agent'),
)

COMPLAINT_STATUS = (
    ('pending', 'Pending'),
    ('work_in_progress', 'Work in progress'),
    ('completed', 'Completed'),
)


class UserProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # additional
    phone_number = PhoneNumberField(max_length=15)
    address1 = models.CharField(max_length=288)
    address2 = models.CharField(max_length=288)
    pin_code = models.CharField(max_length=12)
    city = models.CharField(max_length=124)
    user_type = models.CharField(max_length=20, choices=USER_TYPE, default='customer')

    def save(self, force_insert=False, force_update=False):
        self.city = self.city.lower()
        super(UserProfileModel, self).save(force_insert, force_update)

    def __str__(self):
        return self.user.username


class ComplaintModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Complaint detail
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=1024)
    status = models.CharField(max_length=20, choices=COMPLAINT_STATUS, default='pending')
    created_by = models.CharField(max_length=128)
    created_date = models.DateTimeField(auto_now_add=True)
    solved_by = models.CharField(max_length=128, blank=True)
    solved_date = models.DateTimeField(blank=True, null=True)
    complaint_file = models.FileField(blank=True)

    comments = models.TextField(max_length=300, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('complaint_app:complaint_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


class ComplaintDocument(models.Model):
    complaint = models.ForeignKey(ComplaintModel, on_delete=models.CASCADE)
    file = models.FileField(blank=True)

    def __str__(self):
        return str(self.file)

class ActionModel(models.Model):
    complaint = models.ForeignKey(ComplaintModel, on_delete=models.CASCADE)
    action = models.TextField(max_length=1024)

    def __str__(self):
        return self.action



