from django.contrib import admin
from .models import Friendship

appList = [Friendship]
admin.site.register(appList)
