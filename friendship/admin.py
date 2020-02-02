from django.contrib import admin
from .models import Friendship

lista = [Friendship]
admin.site.register(lista)

# Register your models here.
