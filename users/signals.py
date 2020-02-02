from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Settings


@receiver(post_save, sender=User)
def creatProfile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Settings.objects.create(user=instance)


@receiver(post_save, sender=User)
def saveProfile(sender, instance, **kwargs):
    instance.profile.save()
    instance.settings.save()
