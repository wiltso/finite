from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Todo: REMOVE this at the summer when on one needs then any more
class Timmar(models.Model):
    startdate = models.DateField(default=timezone.now)
    enddate = models.DateField(default=timezone.now)
    starttime = models.TimeField(default=timezone.now)
    endtime = models.TimeField(default=timezone.now)
    title = models.CharField(max_length=100)
    subjecttext = models.TextField('Description', blank=True, null=True)

    frequenseChoise = ((0, 'Only once'),
                       (1, 'Everyday'),
                       (2, 'Every other day'),
                       (3, 'Every three days'),
                       (4, 'Every four days'),
                       (5, 'Every five days'),
                       (6, 'Every six days'),
                       (7, 'Every week'))
    frequense = models.IntegerField(choices=frequenseChoise,
                                    default=0,
                                    help_text='How often do you want this event to happen?')

    user = models.ForeignKey(User, on_delete=models.CASCADE)


# Todo: REMOVE this at the summer when on one needs then any more
class ExcludeTimmar(models.Model):
    starttime = models.TimeField(default=timezone.now)
    date = models.DateField(default=timezone.now)
    time = models.ForeignKey(Timmar, on_delete=models.CASCADE)


class Links(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.TextField(default="")


class Schools(models.Model):
    school_name = models.TextField(default=None, blank=True, null=True)


class Schools_hours(models.Model):
    hourhash = models.TextField(default="")
    startdate = models.DateField(default=timezone.now)
    enddate = models.DateField(default=timezone.now)
    starttime = models.TimeField(default=timezone.now)
    endtime = models.TimeField(default=timezone.now)

    frequenseChoise = ((0, 'Only once'),
                       (1, 'Everyday'),
                       (2, 'Every other day'),
                       (3, 'Every three days'),
                       (4, 'Every four days'),
                       (5, 'Every five days'),
                       (6, 'Every six days'),
                       (7, 'Every week'))
    frequense = models.IntegerField(choices=frequenseChoise,
                                    default=0,
                                    help_text='How often do you want this event to happen?')

    title = models.CharField(max_length=100)
    summary = models.TextField(default="")
    location = models.TextField(default="")
    description = models.TextField(default="")
    resources = models.TextField(default="")
    extra = models.TextField(default="")

    school = models.ForeignKey(Schools, on_delete=models.CASCADE)


class Exclude_schools_hours(models.Model):
    starttime = models.TimeField(default=timezone.now)
    date = models.DateField(default=timezone.now)
    school_hour = models.ForeignKey(Schools_hours, on_delete=models.CASCADE)
