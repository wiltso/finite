from django.db import models
from django.contrib.auth.models import User


class Friendgroup(models.Model):
    groupname = models.CharField(default='', max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')


class Groupmembers(models.Model):
    friendgroup = models.ForeignKey(Friendgroup, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='groupmember')
