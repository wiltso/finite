
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from schedule.views import scheduleOutputDay, scheduleOutputWeek
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime, timedelta
from .models import Profile, Settings
from .forms import (UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
                    SettingsForm, CountryForm)
from friendship.models import Friendship

# Create your views here.


# The view that loads when you are registering a new account
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,
                             f'Your account has been created! Please login ' + str(username))

            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


# The tearms and conditions view
def termsConditions(request):
    return render(request, 'userComponents/termsConditions.html')


# When you add a new friend
@login_required
def addFriend(request, username):
    friend = Friendship(user=request.user, friend=User.objects.filter(username=username).first())
    friend.save()

    # So the other user know they have a pending friends request
    friend.add()
    messages.success(request, f'Friend request has been sent to ' + str(username))
    return redirect('searchForFriends')


# The view when you have set a new password from the mail you get when you click forgotten password
def afterPasswordReset(request):
    messages.success(request, f"Your password has been updated")
    return redirect('login')


# When you remove a friend
@login_required
def removeFriend(request, username):
    Friendship.objects.filter(
        (Q(friend_id=request.user.pk) & Q(user_id=User.objects.get(username=username))) |
        (Q(user_id=request.user.pk) & Q(friend_id=User.objects.get(username=username)))
    ).first().delete()

    messages.warning(request, str(username) + f' is on longer your friend')
    return redirect('searchForFriends')


# The view for your profile
@login_required
def profile(request):
    # Gets the friendships that have been made to you
    friends = Friendship.objects.filter(
        Q(friend_id=request.user.id) &
        Q(pending=True)
    )

    # Gets them to be in the correct format for the frontend
    friendRequests = list(
        map(
            lambda frindShipID: [frindShipID.id, User.objects.get(pk=frindShipID.user.pk)],
            friends
        )
    )

    tohtml = {
        'friendRequests': friendRequests,
        'title': 'Profile'
    }
    return render(request, 'userComponents/profile.html', tohtml)


# Accepts the friend request
@login_required
def acceptFriendRequest(request, pk):
    friendRequest = Friendship.objects.get(pk=pk).accepted()
    return redirect('profile')


# Rejects the friend request
@login_required
def rejectFriendRequest(request, pk):
    friendRequest = Friendship.objects.get(pk=pk).delete()
    return redirect('profile')


# The view for when you make changes to your settings
# Can be to the bio or general settings tho not when you reset your password
@login_required
def settings(request):
    if request.method == 'POST':
        private_form = SettingsForm(request.POST, instance=request.user.settings)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid() and private_form.is_valid():
            private_form.save()
            u_form.save()
            p_form.save()
            return redirect('profile')
        else:
            messages.error(request, "Something did not go as planned, please check our input")

    else:
        private_form = SettingsForm(instance=request.user.settings)
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'private': private_form,
        'u_form': u_form,
        'p_form': p_form,
        'title': 'Settings',
    }
    return render(request, 'users/settings.html', context)


# The view for changeing your password
@login_required
def changePassword(request):
    if request.method == 'POST':
        passwd_form = PasswordChangeForm(request.user, request.POST)
        if passwd_form.is_valid():
            passwd_form.save()
            update_session_auth_hash(request, request.user)
            return redirect('profile')
        else:
            messages.error(request, "Something did not go as planned, please check our input")

    else:
        passwd_form = PasswordChangeForm(request.user)

    context = {
        'passwd_form': passwd_form,
        'title': 'Change Password'
    }
    return render(request, 'users/password.html', context)


# View for when you go and view a persons profile
@login_required
def seeProfile(request, username):
    Me = Profile.objects.get(user_id=request.user.id)
    they = User.objects.get(username=username)
    if request.method == 'POST':
        status = request.POST.get('friendShipStatus')
        if status == 'bff':
            if len(Me.bff.all()) >= 6:
                messages.warning(request, f'You can only have 6 best friends please remove one then you can add a new best friend')
                return redirect('listBFFfriends')
            Me.bff.add(they)
            Me.save()
        elif status == 'f':
            Me.bff.remove(they)
            Me.save()
    if Me.bff.filter(id=they.id):
        status = 'bff'
    else:
        status = 'f'

    variable = {
        'form': CountryForm(initial={'friendShipStatus': status}),
        'cansee': not Settings.objects.get(user_id=User.objects.get(username=username).pk).private,
        'output': "",
        'schedules': {"schedule1": '1'},
        'thefriend': User.objects.get(username=username),
        'friend': False,
        'pending': False
    }
    friendship = Friendship.objects.filter(
        (Q(friend=variable['thefriend'].pk) & Q(user=request.user.pk)) |
        (Q(friend=request.user.pk) & Q(user=variable['thefriend'].pk))
    )

    for i in friendship:
        variable['friend'] = True
        variable['cansee'] = True
        if i.pending is True:
            variable['pending'] = True

    if variable['cansee'] is False or variable['pending'] is True:
        variable['cansee'] = False
        return render(request, 'users/seeprofile.html', variable)

    variable['output'] = scheduleOutputWeek(they)

    schedules = {}
    for i in range(len(variable['output']['they'])):
        schedules['schedule'+str(i)] = str(i)

    variable['schedules'] = schedules

    return render(request, 'users/seeprofile.html', variable)

# View for when there has been a update to the tearms and conditions
@login_required
def newTearms(request):
    if not request.user.profile.acceptedlatest:
        return render(request, 'userComponents/newTearms.html')
    else:
        return redirect('home')


# When you accept the new tearms and conditions
@login_required
def acceptedNewTearms(request):
    Profile.objects.filter(user_id=request.user.id).update(acceptedlatest=True)
    return redirect('home')


# The view when you click on a day when you are a viewing the persons schedule
@login_required
def compareSchedules(request, username, day):
    datetoday = datetime.date(datetime.now() + timedelta(days=day, hours=-3))
    mindate = datetime.date(datetime.now() + timedelta(days=-8, hours=-3))
    maxdate = datetime.date(datetime.now() + timedelta(days=8, hours=-3))

    if mindate <= datetoday <= maxdate:
        pass
    else:
        return HttpResponse("<h1>Don't think i didn't think of this you littel **** I VALUE PRIVACY</h1>")

    test = scheduleOutputDay([request.user], day)
    for key in test['they'][0][0].keys():
        my = test['they'][0][0][key]
    output = {'My': my}

    # Gets the schedules for the friends
    test = scheduleOutputDay([User.objects.get(username=username)], day)
    output['they'] = test['they']

    # Counts the amount of schedules generated
    schedules = {}
    for i in range(len(output['they'])):
        schedules['schedule'+str(i)] = str(i)

    tohtml = {
        'output': output,
        'schedules': schedules,
        'day': day,
        'nextday': day+1,
        'beforeday': day-1,
        'username': username,
        'date': datetoday,
        'where': 'compareSchedule',
        'title': 'Schedule comparison'
    }

    return render(request, 'scheduleComponents/compareschedules.html', tohtml)
