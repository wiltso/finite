from django.db import models
from groups.models import Friendgroup, Groupmembers
from django.contrib.auth.models import User
from django.db.models import Q
from users.models import Profile


class Friendship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend')
    pending = models.BooleanField(default=True, null=False)

    def add(self):
        friend = User.objects.get(pk=self.friend.pk)
        friend.profile.friendRequest += 1
        friend.save()

    def delete(self, *args, **kwargs):
        friend = Profile.objects.get(pk=self.friend.id)
        Me = Profile.objects.get(user_id=self.user.id)
        # Removes the friend request if there is one
        if self.pending:
            friend.friendRequest -= 1

        # Removes the users from there Bff list
        # This is to prevent so if you remove a friend you can get a new bff
        Me.bff.remove(friend.user)
        friend.bff.remove(Me.user)

        # Removes the friends from groups if when they unfriend
        def remove(group):
            if len(Groupmembers.objects.filter(friendgroup=group)) == 1:
                group.delete()
            else:
                Groupmembers.objects.filter(friendgroup=group).delete()

        # Calls the remove function
        # The hole thing needs to be in the list function so it runs the map function
        # This is due to pythons laysiness
        list(map(remove, list(Friendgroup.objects.filter(Q(owner=Me.user) &
                                                         Q(groupmembers__member=friend.user)))))

        list(map(remove, list(Friendgroup.objects.filter(Q(owner=friend.user) &
                                                         Q(groupmembers__member=Me.user)))))

        # Saves profiles
        Me.save()
        friend.save()

        super(Friendship, self).delete(*args, **kwargs)

    def accepted(self, *args, **kwargs):
        friend = User.objects.get(pk=self.friend.pk)
        friend.profile.friendRequest -= 1
        friend.save()
        self.pending = False
        super(Friendship, self).save(*args, **kwargs)
