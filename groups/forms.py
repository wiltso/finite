from django.db.models import Q
from groups.models import Friendgroup
from django import forms


class GroupNameForm(forms.Form):
    def fillData(self, groupName, *args, **kwargs):
        self.initial['name'] = groupName
        self.fields['name'].label = "Change the name of the group?: "

    def checkForSameName(self, userId, old_name, *args, **kwargs):
        if self.is_valid():
            usersSameName = Friendgroup.objects.filter(Q(groupname=self.cleaned_data['name'])
                                                       & Q(owner_id=userId)).count()
            if usersSameName == 0 or (usersSameName == 1 and old_name == self.cleaned_data['name']):
                return True
        return False

    name = forms.CharField(label="Set a name for the group: ", max_length=50, required=True)


class GroupMemberFrom(forms.Form):
    def fillData(self, friends, *args, **kwargs):
        CHOICES = ((user.username, user.username) for user in friends)
        self.fields['selectedFriends'].choices = CHOICES

    def myClean(self, friends):
        friends = self.cleanFriends(friends)
        realfriends = []
        for i in self.data:
            if i in friends:
                realfriends.append(str(i))

        if len(realfriends) > 0:
            return realfriends

        else:
            return False

    def cleanFriends(self, friendsList):
        friends = []
        for i in friendsList:
            friends.append(i['username'])
        return friends

    def setLabel(self, label):
        self.fields['selectedFriends'].label = label

    selectedFriends = forms.MultipleChoiceField(label="Select all the friends you want in your group",
                                                widget=forms.CheckboxSelectMultiple())
