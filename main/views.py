from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from reporting.getreportdata import getStats
from friendship.models import Friendship
from django.shortcuts import render, redirect
from django.db.models import Q
from schedule.views import scheduleOutputDay
from django.contrib import messages
from mail.sendMail import sendMail
from users.models import Profile
from django.http import HttpResponse
from datetime import datetime, timedelta


# TODO: Get the error pages up
def error_404(request, e):
    return render(request, 'main/error.html')


def error_500(request):
    return render(request, 'main/error.html', status=500)


# This view is the first one to load when you come to finite
def home(request):
    if str(request.user) == "AnonymousUser":
        return gotToFront(request)
    else:
        return listSchedules(request, 0)


# The view to the front page
def gotToFront(request):
    return render(request, 'main/frontpage2.html')


# For admin to get stats of usage
def sendReports(request):
    if request.user.is_superuser:
        sendMail(getStats())
    return redirect(home)

# The view that is loaded when you go to home
# It takes the request and the day you want to be shown
@login_required
def listSchedules(request, day):
    # If you don't have imported your schedule
    if (request.user.profile.age == "" or request.user.profile.age == "0") and request.user.profile.allinfo == '':
        messages.warning(request, f'Please go to "Import your schedule" and paste in your Wilma url(To find instruction click the link "Where do I find my wilma URL?")')

    # To ensure that pepole don't get stalk to far in to the futher
    datetoday = datetime.date(datetime.now() + timedelta(days=day, hours=-3))
    mindate = datetime.date(datetime.now() + timedelta(days=-2, hours=-3))
    maxdate = datetime.date(datetime.now() + timedelta(days=8, hours=-3))

    if mindate <= datetoday <= maxdate:
        pass
    else:
        return HttpResponse("<h1>Don't think I didn't think of this you littel **** I VALUE PRIVACY</h1>")
    # Gets all of the friends of the requesting user
    friend = list(
        Friendship.objects.filter(
            Q(user_id=request.user.pk) |
            Q(friend_id=request.user.pk)
        ).filter(pending=False)
    )

    allowedUser = []
    for i in friend:
        if i.friend.pk == request.user.pk:
            allowedUser.append(i.user)
        else:
            allowedUser.append(i.friend)

    # Gets the schedule for the requesting user
    test = scheduleOutputDay([request.user], day)
    for key in test['they'][0][0].keys():
        my = test['they'][0][0][key]
    my[0]['day'] = my[0]['day'] - 1
    output = {'My': my}

    if len(allowedUser) == 0:
        messages.info(request, f'Get your friends using Finite and add them as your friends. Then you will be able to see your schedule')

    # Sorts the requesting users friends first bbf then the rest
    firstbff = 0
    Me = Profile.objects.get(user_id=request.user.id)
    for i in allowedUser:
        they = User.objects.get(id=i.pk)
        if Me.bff.filter(id=they.id):
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
    print(schedules)
    tohtml = {
        'output': output,
        'schedules': schedules,
        'day': day,
        'nextday': day+1,
        'beforeday': day-1,
        'date': datetoday,
        'where': 'schedule',
        'title': "Home",

    }

    return render(request, 'main/home.html', tohtml)
