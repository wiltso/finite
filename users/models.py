from django.db import models
from django.contrib.auth.models import User
from schedule.models import Schools_hours
from PIL import Image

# Create your models here.


class Profile(models.Model):
    version = models.IntegerField(default=1)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='Profile_images')

    friendRequest = models.IntegerField(default=0, null=False)

    realname = models.TextField(default='', blank=True)
    realclass = models.TextField(default='', blank=True)
    age = models.TextField(default='', blank=True)
    school = models.TextField(default='', blank=True)

    hours = models.ManyToManyField(Schools_hours, default=None, blank=True)

    allinfo = models.TextField(default='', blank=True)
    latestlink = models.TextField(default='', blank=True)

    accessamount = models.IntegerField(default=0, blank=True)
    last_access = models.DateTimeField(null=True)

    importsuccess = models.BooleanField(default=False)
    acceptedlatest = models.BooleanField(default=True)

    bio = models.TextField(
        'Bio',
        default='',
        help_text="Make your account more personal with a bio",
        blank=True,
        null=True,
        max_length=500
    )
    bff = models.ManyToManyField(User, default=None, related_name='bff', blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    # Makes sure that the profile images is not too big
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        width, height = img.size
        if width > height:
            left = width / 2 - height / 2
            top = 0
            right = width / 2 + height / 2
            bottom = height
            img = img.crop((left, top, right, bottom))
        elif width < height:
            left = 0
            top = height / 2 - width / 2
            right = width
            bottom = height / 2 + width / 2
            img = img.crop((left, top, right, bottom))
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
        img.save(self.image.path)


class Settings(models.Model):
    private = models.BooleanField(
        'Private profile?',
        default=True,
        help_text="This is a setting that you can trun on so pepole can not see you schedule if they are not your friend"
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
