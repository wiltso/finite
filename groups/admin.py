from django.contrib import admin
from .models import Friendgroup, Groupmembers

appList = [Friendgroup, Groupmembers]
admin.site.register(appList)
