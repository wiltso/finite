from django.contrib import admin
from .models import Profile, Settings
# Register your models here.

appList = [Profile, Settings]
admin.site.register(appList)
