from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from friendship.models import Friendship
from friendship.views import baseQuery
from django.shortcuts import render, redirect
from django.db.models import Q
from schedule.views import scheduleOutputDay
from groups.models import Friendgroup, Groupmembers
from users.models import Profile
from groups.forms import GroupMemberFrom, GroupNameForm
from django.http import HttpResponse
from datetime import datetime, timedelta


def baseFriendQuery(request):
    return baseQuery(request).filter(
        Q(user__in=Friendship.objects.filter(friend_id=request.user.id).exclude(pending=True)) |
        Q(friend__in=Friendship.objects.filter(user_id=request.user.id).exclude(pending=True))
    )


# List all of the groups you have created
@login_required
def Listgroups(request):
    groups = Friendgroup.objects.filter(owner=request.user).values('groupname').distinct()
    tohtml = {
        'title': 'Groups',
        'groups': groups,
    }
    return render(request, 'groups/listgroups.html', tohtml)


# The view for creating groups
# For now it's just for creating the private groups
@login_required
def creatGroup(request):
    # Gets the persons friends
    friends = baseFriendQuery(request)

    # Makes the group name form so it can set the titel late if one is submitted
    group_name = GroupNameForm()

    # the message varibel for the info to the user
    messages = ""

    # If there is a form that  is submitted
    if request.method == "POST":
        # Gets all the info from the request
        name = GroupNameForm(request.POST)
        members = GroupMemberFrom(request.POST.getlist('selectedFriends'))

        # Sets the name of the name field to what the user submitted
        group_name.fillData(str(request.POST.get('name')))

        # checks the the user dosen't have any same named groups that cloud cause a problem
        if name.checkForSameName(request.user.id, ''):

            # Cleans ut all the users usernams form the submitted form
            # Checks that is't a friend of yours
            # Returns False if there is any problem
            selectedFriends = members.myClean(friends.values('username'))

            # If everything is okej if will creat the group and add all of the members
            if selectedFriends:
                group = Friendgroup(groupname=name.cleaned_data['name'], owner=request.user)
                group.save()
                for member in selectedFriends:
                    Groupmembers(friendgroup=group, member=User.objects.get(username=member)).save()

                # Then take you to the group
                return redirect('seeGroup', day=0, group_name=str(request.POST.get('name')))

            else:
                # If pepole have not selected any friends
                messages = ['No friends!', ["You have not selected any friends"]]
        else:
            # If the user already have a group with that name
            messages = ['Sorry!', ['You already have a group with that name']]

    # If you have no friends you will be redirected to my friends
    # Where there is more info for how to get friends
    if len(friends) == 0:
        return redirect('listfriends')

    # Makes the friend form
    Group_member_from = GroupMemberFrom()
    Group_member_from.fillData(friends)

    tohtml = {
        'changeNameForm': group_name,
        'MembersForm': Group_member_from,
        'title': 'Create group',
        'submitText': 'Create the group',
        'messagesToUser': messages
    }

    return render(request, 'groupsComponents/changeGroups.html', tohtml)


# The view that is loaded when you go to a specific group
# It takes the request and the day you whant to be shown and the groupname
@login_required
def seeGroup(request, group_name, day):
    # Gets the dates of the days that are on the end of the limite you can you a persons schedule
    datetoday = datetime.date(datetime.now() + timedelta(days=day, hours=-3))
    mindate = datetime.date(datetime.now() + timedelta(days=-1, hours=-3))
    maxdate = datetime.date(datetime.now() + timedelta(days=8, hours=-3))

    # Checks that the request is in the give min and max date
    if mindate <= datetoday <= maxdate:
        pass
    else:
        return HttpResponse("<h1>Don't think i didn't think of this you littel **** I VALUE PRIVACY</h1>")

    # Gets all of the users that are in the group
    group = Friendgroup.objects.get(Q(owner=request.user) & Q(groupname=group_name))
    allowedUserId = list(
        map(lambda x: x['member'],
            Groupmembers.objects.filter(friendgroup_id=group.id).values('member'))
    )

    allowedUser = []
    for id in allowedUserId:
        allowedUser.append(User.objects.get(id=id))

    # Gets the schedule for the requesting user
    test = scheduleOutputDay([request.user], day)
    for key in test['they'][0][0].keys():
        my = test['they'][0][0][key]
    output = {'My': my}

    # Sorts the requesting users friends first bbf then the rest
    firstbff = 0
    Me = Profile.objects.get(user_id=request.user.id)
    for i in allowedUser:
        they = User.objects.get(id=i.pk)
        if Me.bff.all().filter(id=they.id):
            index = allowedUser.index(they)
            allowedUser[firstbff], allowedUser[index] = allowedUser[index], allowedUser[firstbff]
            firstbff += 1

    # Gets the schedules for the friends
    test = scheduleOutputDay(allowedUser, day)
    output['they'] = test['they']

    # Counts the amount of schedules generated
    schedules = {}
    for i in range(len(output['they'])):
        schedules['schedule' + str(i)] = str(i)

    tohtml = {
        'output': output,
        'title': group_name,
        'schedules': schedules,
        'day': day,
        'nextday': day + 1,
        'beforday': day - 1,
        'groupname': group.groupname,
        'date': datetoday,
        'where': 'seeGroup',
    }

    return render(request, 'groups/groupschedule.html', tohtml)


# Adds members to the group
# Can alosw change the name of the group
@login_required
def addGroupMember(request, group_name):
    # Gets all of the persons friends that are not in the group
    friends = baseFriendQuery(request).exclude(
        id__in=[i.member.id for i in Groupmembers.objects.filter(
            friendgroup_id=Friendgroup.objects.get(Q(owner_id=request.user.id) &
                                                   Q(groupname=group_name)).id
            )
        ]
    )

    # Creats the group name form and sets the input value to what it is right now
    group_name_form = GroupNameForm()
    group_name_form.fillData(str(group_name))

    # Sets the title of the page
    messages = ''
    title = 'Add friends'

    # If the is a form that is submitted
    if request.method == "POST":
        # Makes the forms with the data submitted form the form
        name = GroupNameForm(request.POST)

        # NEEDS TO BE getlist so that all members that are selected will be added
        members = GroupMemberFrom(request.POST.getlist('selectedFriends'))

        # Gets the new group name from the request
        # It can be the same as the old on
        new_group_name = str(request.POST.get('name'))
        group_name_form.fillData(new_group_name)

        # checks the the user dosen't have any same named groups that cloud cause a problem
        if name.checkForSameName(request.user.id, group_name):

            # Sets the group name the the new group name this
            # If thay are the same nothing happens
            group = Friendgroup.objects.get(Q(groupname=group_name) & Q(owner=request.user))
            group.groupname = new_group_name
            group.save()

            # Cleans ut all the users usernams form the submitted form
            # Checks that they are friends with you
            # Returns False if there is any problem
            selectedFriends = members.myClean(friends.values('username'))

            # If everything is okej if will creat the group
            if selectedFriends:

                # Every member selected gets added to the group
                for member in selectedFriends:
                    Groupmembers(friendgroup=group, member=User.objects.get(username=member)).save()

                # Returns you to the groups schedule
                return redirect('seeGroup', day=0, group_name=new_group_name)
            else:
                # Returns you to the groups schedule
                return redirect('seeGroup', day=0, group_name=new_group_name)
        else:
            # If the person already has a group with that name
            messages = ['Sorry!', ['You already have a group with that name']]

    if len(friends) > 0:
        # If you have friends that are not in the group they will be added
        Group_member_from = GroupMemberFrom()
        Group_member_from.fillData(friends)
    else:
        # If all of your friends are in the group already
        Group_member_from = ''
        messages = ['No friends', ['All of your friends', 'are in this group already']]
        title = 'Change group name'

    tohtml = {
        'changeNameForm': group_name_form,
        'MembersForm': Group_member_from,
        'title': title,
        'submitText': 'Make changes',
        'messagesToUser': messages
    }
    return render(request, 'groupsComponents/changeGroups.html', tohtml)


# Removes members from the group
# It can be one or many mambers
# You can alsow change the name of the group
@login_required
def removeGroupMember(request, group_name):
    # Gets all of the persons friends that are not in the group
    friends = baseQuery(request).filter(id__in=[
        i.member.id for i in Groupmembers.objects.filter(
            friendgroup_id=Friendgroup.objects.get(
                Q(owner_id=request.user.id) &
                Q(groupname=group_name)
            ).id
        )
    ])

    # Creats the group name form and sets the value of the input field to what the name is now
    group_name_form = GroupNameForm()
    group_name_form.fillData(str(group_name))

    # Sets the title of the page
    messages = ['Remember!', ["If you remove all group members", "the group will get deleted!"]]
    title = 'Remove friends'

    # if a form is submitted
    if request.method == "POST":
        # Makes the forms with the data submitted form the form
        name = GroupNameForm(request.POST)

        # NEEDS TO BE getlist so that all members that are selected will be added
        members = GroupMemberFrom(request.POST.getlist('selectedFriends'))

        # Sets the value of the input field to what the new name is
        new_group_name = str(request.POST.get('name'))
        group_name_form.fillData(new_group_name)

        # checks the the user dosen't have any same named groups that cloud cause a problem
        if name.checkForSameName(request.user.id, group_name):

            group = Friendgroup.objects.get(Q(groupname=group_name) & Q(owner=request.user))
            group.groupname = new_group_name
            group.save()

            # Cleans ut all the users usernames form the submitted form
            # Checks that they are friends
            # Returns False if there is any problem
            selectedFriends = members.myClean(friends.values('username'))

            # If there are no friends selected it will just return you to the groups schedule
            if not selectedFriends:
                return redirect('seeGroup', day=0, group_name=new_group_name)

            # If everything is okej if will creat the group
            if len(selectedFriends) < len(friends):
                for member in selectedFriends:
                    Groupmembers.objects.get(
                        friendgroup=group,
                        member=User.objects.get(username=member)
                    ).delete()

                # After all friends that have been removed and there are still members
                # It returns you to the groups schedule
                return redirect('seeGroup', day=0, group_name=new_group_name)
            else:
                # If all friends are deleted from the group the group will be deleted
                group.delete()
                return redirect('listgroups')
        else:
            # If you have another group with the same name
            messages = ['Typo?', ['You already have a group with that name']]

    if len(friends) > 0:
        # Fills in the members that you can remove
        Group_member_from = GroupMemberFrom()
        Group_member_from.fillData(friends)
        Group_member_from.setLabel('Select the friends you want to remove')
    else:
        # This should never run but if you have no friends in the group and whant to remove them
        Group_member_from = ''
        messages = ['No friends', ['All of your friends', 'are in this group already']]
        title = 'Change group name'

    tohtml = {
        'changeNameForm': group_name_form,
        'MembersForm': Group_member_from,
        'title': title,
        'submitText': 'Make changes',
        'messagesToUser': messages
    }
    return render(request, 'groupsComponents/changeGroups.html', tohtml)


# Deletes the group and all of the related things AKA all of its members from this group
# Thats you back to where all of your groups are
@login_required
def deleteGroup(request, group_name):
    Friendgroup.objects.get(Q(groupname=group_name) & Q(owner=request.user)).delete()
    return redirect('listgroups')
