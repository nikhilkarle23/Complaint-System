from django.contrib import admin
from complaint_app.models import UserProfileModel, ComplaintModel

# Register your models here.
admin.site.register(UserProfileModel)
admin.site.register(ComplaintModel)