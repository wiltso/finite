from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from schedule.models import (Timmar, ExcludeTimmar, Links, Schools,
                             Schools_hours, Exclude_schools_hours)
from django.contrib import messages
from mail.sendMail import sendMail
from users.models import Profile
from django.conf import settings
from icalendar import Calendar
from security import hashing, crypting
from datetime import datetime, timedelta
from .forms import WilmaURLForm
from urllib import request
from friendship.models import Friendship
from django.shortcuts import render


# The instructions view for where to get your link
@login_required
def importScheduleInstructions(request):
    tohtml = {
        'title': 'Wilma link instructions'
    }
    return render(request, 'schedule/wilmaImportInstructions.html', tohtml)


# The view for when you import your schedule
@login_required
def importSchedule(request):
    if request.method == 'POST':
        form = WilmaURLForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['url']:
                getWilmaData(form.cleaned_data['url'], request)
            else:
                importIcsFile(form.cleaned_data['file'], request)

    else:
        form = WilmaURLForm()

    friends = Friendship.objects.filter(
        Q(friend_id=request.user.id) &
        Q(pending=True)
    )

    friendRequests = []
    for i in friends:
        temp = []
        temp.append(i.pk)
        temp.append(User.objects.get(pk=i.user.pk))
        friendRequests.append(temp)

    tohtml = {
        'friendRequests': friendRequests,
        'form': form,
        'title': 'Get connected'
    }

    return render(request, 'schedule/wilmaImportSchedule.html', tohtml)


# Takes the link hashes it and then compares it against all other links
# If there are no other same links it's fine
# If there are other same links from other users if will compare it more deeply
def compareLinks(link, user, opendLink) -> bool:
    # Hashes the link
    hashedLink = getHashedLink(link)

    # Checks for the links
    sameLink = Links.objects.filter(link=hashedLink).exclude(
        user_id=user.id).values('user').distinct()
    if not sameLink:
        return False
    else:
        # Returns the answer of the more thero check
        return compareSameLinks(opendLink,
                                User.objects.get(id=sameLink[0]['user']), user)


# Takes the link and takes away the parts that can change in the link
# Then hashes it
def getHashedLink(link):
    link = link.split('/')[:-1]
    correctLink = ""
    for i in link:
        correctLink += i
    hashedLink = hashing.hashing(correctLink, settings.LINK_HASH)
    return hashedLink


# Gets all of the events from the calender
def getEvents(link):
    gcal = Calendar.from_ical(link)
    events = []

    # Removes all of the extra data that is not a event aka an hour on the schedule
    for i in gcal.walk():
        if i.name == 'VEVENT':
            events.append(i)

    return events


# Gets the link with the highest priority from the link
def getBiggestLink(events):
    correctLink = {}
    for i in events:
        try:
            correctLink[events[0]['UID']] += 1
        except KeyError:
            correctLink[events[0]['UID']] = 1
    biggesLink = sorted(correctLink.items(), key=lambda kv: kv[1])
    biggesLink = biggesLink[::-1]
    return biggesLink[0][0]


# The better security check for the link if they are the same
# This should not run that often
def compareSameLinks(link, pastLinkOwner, requestingUser) -> bool:
    print("BETTER LINK COMPARISON")
    personIs = getBiggestLink(getEvents(link)).split('/')[1:-1]
    # Encrypts the users realname
    realname = personIs[1].split(' ')[1] + " " + personIs[1].split(' ')[2]

    # Encrypts the witch class the user is on
    realclass = personIs[1].split(' ')[0]

    if realname == crypting.decrypt(
            pastLinkOwner.profile.realname,
            settings.CRYPTION_PASS_2) and realclass == crypting.decrypt(
                pastLinkOwner.profile.realclass, settings.CRYPTION_PASS_2):
        print(
            "'" +
            requestingUser.username +
            "' ID:(" + str(requestingUser.id) +
            ") has tryed to add '" +
            pastLinkOwner.username +
            "' ID:(" +
            str(pastLinkOwner.id) +
            ") schedule"
        )

        return True
    else:
        print("There is a new owner for this schedule link")
        Links.objects.filter(user_id=pastLinkOwner.id).delete()
        return False


# This function is the first line of defence against urls that are not wilmas links
# It also checks that it gets a 200 respones from the seerver
def getWilmaData(url, userRequest):
    # Security checks that here are few things in the link
    if 'https://' in url and '/schedule/export/' in url and 'Wilma.ics?' in url:
        print("Success full wilma link " + str(url))
        # makes the request to the url
        r = request.urlopen(url)

        if r.code == 200:
            data = r.read()
            if compareLinks(url, userRequest.user, data):
                messages.warning(
                    userRequest, f"""
                    Do not import other pepoles schedule that is not your information.
                    You have been warned!!
                    """)
            else:
                link, created = Links.objects.get_or_create(user=userRequest.user,
                                                            link=getHashedLink(url))
                ICSApi(data, userRequest, url)
        else:
            messages.warning(
                userRequest, f"""
            Looks like there was a problem with Wilma, please try again later!
            """)

    # If the security checks fails
    else:
        print("Faild wilma link " + str(url))
        # Let's the user know what was proploply wrong with the link
        messages.warning(
            userRequest, f"""
        The link was not a vaild link, please remember that it needs to start with https://
        """)


# Gets the personal data from the events and save them to the profile
# It returns a school object and the mail content
def fillPersonalData(events, userRequest, url):
    # To get information about the user so it can suggest friends for you better
    mailcontent = "User " + str(
        userRequest.user.pk) + " has added their schedul."
    school = ""
    realname = ""
    realclass = ""
    age = ""
    try:
        # Gets the biggest link and make it in to an array where the info is
        biggest_link = getBiggestLink(events)
        biggestLink = biggest_link.split('/')[1:-1]

        # Gets the class the person is on
        # There have been 2 ways to get it depends a bit on the wilma
        # This is the first place to change if there is something wrong with a new schools imports
        realclass = ''
        if len(biggestLink) == 2:
            realclass = biggestLink[-1].split(' ')[0]
        elif len(biggestLink) == 3:
            realclass = biggestLink[1]
        else:
            raise ValueError(
                'The length of the allinfo link is: ' +
                str(len(biggestLink)) +
                " this is a new length and can not be prossesed. Biggest link for debuging: ",
                biggestLink
            )

        # Gets the name of the person
        # The name has to this point always been in the last place of the array
        name = biggestLink[-1].split(' ')[1:]
        realname = ''
        for i in name:
            realname += i + " "
        realname = realname[:-1]

        # Checks that the name is the correct length
        if len(realname.split(' ')) not in [2, 3]:
            raise ValueError('The length of the name is wrong here is the name: ' +
                             realname +
                             " Here is the biggest link for debuging",
                             biggestLink)

        # First_cat is the first part of the array is where the year of the school is
        # There can be the schools name.
        first_cat = biggestLink[0].split(' ')
        school = ""
        # Checks that the school name is the school name with a higher cetrenty
        if all(list(map(lambda element: 'Lukiokoulutus' not in element, first_cat))):
            # If there is more then just the date it will get the school
            if len(first_cat) > 1:
                for i in first_cat:
                    if '-' in i or i == '':
                        continue
                    else:
                        school += i + " "
                school = school[:-1]
            # If there is just the date it will set the school to what the link is
            elif len(first_cat) == 1:
                url = url[8:]
                url = url.split('/')[0]
                school = str(url)
                mailcontent += "\nThe school did not go true is now: " + school
            # Hopfully will never run
            else:
                url = url[8:]
                url = url.split('/')[0]
                school = str(url)
                mailcontent += "\nWe got a problem with the school: " + school
        # If It belives that the school is not in the link it will use whats in the url
        else:
            url = url[8:]
            url = url.split('/')[0]
            school = str(url)

        # Trys to get the age from the class you are on
        age = ''
        for i in realclass:
            # Some schools have some letters befor the numbers witch tells you what there age is
            if len(age) > 0 and not i.isdigit():
                break
            elif i.isdigit():
                age += i

        # Some schools just gives the class as example 1B
        # Then it checks witch school year it is like 2019-2020
        # Then make the best guess of your age
        year = ''
        if len(age) == 1:
            # Gets the schools years first half
            for i in biggestLink[0]:
                if len(year) > 0 and not i.isdigit():
                    break
                elif i.isdigit():
                    year += i
            # If someone was on the second year this will make sure that the age is correct
            age = str(int(year) - (int(age) - 1))
        # If the age is just 2 letters long it will add 2000 to it so every one
        # Has the same age that are the same age
        elif len(age) == 2:
            age = str(int(age) + 2000)

        # It should be fine but it will add the warning to the mail
        elif len(age) == 4:
            age = str(age)
            mailcontent += "\nThe age is might be wrong: " + age

        # So it wont get stuck but will send alert in the mail
        else:
            age = str(age)
            mailcontent += "\nThe age is wrong: " + age

        # Hashes and crypts everything
        hashed_real_school = hashing.hashing(school, settings.SCHOOL_HASH)
        hashed_real_age = hashing.hashing(age, settings.AGE_HASH)
        crypted_real_name = crypting.encrypt(realname, settings.CRYPTION_PASS_2)
        crypted_real_class = crypting.encrypt(realclass, settings.CRYPTION_PASS_2)

    except ValueError as e:
        print(e)
        print("THERE IS MOST LIKLY A ERROR\n\n\n")
        mailcontent += str(e)
    except Exception as e:
        print(e)
        print("SOMETHING WHENT HORROBOLY WRONG\n\n\n")
        mailcontent += "\nSomething whent HORROBOLY WRONG"
    else:
        # Adds the user data if it was in the corrcet format
        mailcontent += "\nThis was a success by the system"
        mailcontent += "\nClass: {} Age: {} School: {}".format(realclass,
                                                               age,
                                                               school)
        print("Name: {}\nClass: {}\nAge: {}\nSchool: {}".format(realname,
                                                                realclass,
                                                                age,
                                                                school))
        profil = User.objects.get(pk=userRequest.user.pk)
        profil.profile.realname = crypted_real_name
        profil.profile.realclass = crypted_real_class
        profil.profile.age = hashed_real_age
        profil.profile.school = hashed_real_school
        profil.profile.importsuccess = True
        profil.save()
    finally:
        if school == '' or school is None or isinstance(school, int) or isinstance(school, bool):
            school = str(userRequest.user.pk)
        hashed_school = hashing.strongHashing(school, settings.SCHOOL_CRYPTION)

    print(str(school) + ": Got hashed to: " + hashed_school)
    school, created = Schools.objects.get_or_create(school_name=hashed_school)
    if created:
        mailcontent += "\nNew school was created"

    # Addes the link to the database encrypted
    # This is so if something gose to shit
    # We can figure out what whent wrong and inpruve the service
    profil = User.objects.get(pk=userRequest.user.pk)
    profil.profile.allinfo = crypting.encrypt(biggest_link, settings.CRYPTION_PASS_3)
    profil.profile.latestlink = crypting.encrypt(url, settings.CRYPTION_PASS_3)
    profil.profile.version = 2
    profil.save()

    return mailcontent, school


def hourHash(hour, mailcontent):
    hash_str = ""
    hasExclude = False
    for j in hour:
        # Gets the start time and date
        if j == 'DTSTART':
            hash_str += "Start datetime: " + str(hour[j].dt)

        # Gets the end time and date
        elif j == 'DTEND':
            hash_str += "End datetime: " + str(hour[j].dt)

        # If the event has a date that it will be excluded this will run a loop futer down
        elif j == 'EXDATE':
            hasExclude = True

        # If The event will run for many weeks
        elif j == 'RRULE':
            for rules in hour[j]:
                for k in hour[j][rules]:
                    if rules == 'UNTIL':
                        # Updates the end date
                        hash_str += "New enddate: " + str(k)
                    # The frequensy of the event happening
                    elif rules == 'FREQ':
                        # Need to add better frequensy
                        hash_str += "Frequense of the hour: " + str(k)

        # Gets the information like what lesson it is
        elif j == 'SUMMARY':
            hash_str += "The hours summary is: " + str(hour[j])
        elif j == 'LOCATION':
            hash_str += "Location for the hour: " + str(hour[j])
        elif j == 'DESCRIPTION':
            hash_str += "Description of the hour: " + str(hour[j])
        elif j == 'RESOURCES':
            hash_str += "Witch resaourses are needed: " + str(hour[j])
        else:
            if j not in ['UID', 'DTSTAMP', 'CATEGORIES']:
                mailcontent += "\nThere is a new parameter in the link:" + str(j)

    # Makes all of the exclud hours
    # Makes a new excluded hour for every time it's excluded
    if hasExclude:
        for j in hour['EXDATE'].dts:
            hash_str += "The excluded hours: " + str(j.dt)

    hashed = hashing.strongHashing(hash_str, settings.SCHOOL_CRYPTION)

    return hashed, mailcontent


# Walks true every event that came from the wilma link.
# Adds every hour as a new hour to the database for the user
def ICSApi(data, userRequest, url):
    # Make the request into a calender object
    events = getEvents(data)

    mailcontent, school = fillPersonalData(events, userRequest, url)

    personal_password = hashing.strongHashing(userRequest.user.username,
                                              userRequest.user.date_joined)

    new_hours = 0
    old_hours = 0

    # Adds every event one at a time
    for i in events:
        hour_hash, mailcontent = hourHash(i, mailcontent)
        hour = Schools_hours.objects.filter(Q(hourhash=hour_hash))
        if len(hour) == 1:
            userRequest.user.profile.hours.add(hour[0])
            old_hours += 1
        else:
            new_hours += 1
            school_hour = Schools_hours()
            school_hour.hourhash = hour_hash
            school_hour.school = school
            hasExclude = False
            extra_text = ""
            for j in i:
                # Gets the start time and date
                if j == 'DTSTART':
                    school_hour.startdate = datetime.date(i[j].dt)
                    school_hour.starttime = datetime.time(i[j].dt)

                # Gets the end time and date
                elif j == 'DTEND':
                    school_hour.endtime = datetime.time(i[j].dt)
                    school_hour.enddate = datetime.date(i[j].dt)

                # If the event has a date that it will be excluded this will run a loop futer down
                elif j == 'EXDATE':
                    hasExclude = True

                # If The event will run for many weeks
                elif j == 'RRULE':
                    for rules in i[j]:
                        for k in i[j][rules]:
                            if rules == 'UNTIL':
                                # Updates the end date
                                school_hour.enddate = k
                            # The frequensy of the event happening
                            elif rules == 'FREQ':
                                # Need to add better frequensy
                                if k == 'WEEKLY':
                                    school_hour.frequense = 7
                                else:
                                    school_hour.frequense = 10
                                    mailcontent += "\nUnknown hour frequense"

                # Gets the information like what lesson it is
                elif j == 'SUMMARY':
                    school_hour.summary = crypting.encrypt(str(i[j]), personal_password)
                    t = str(i[j]).split('(')
                    if len(t) == 3:
                        t = t[0]
                    else:
                        t = t[0]

                    mailcontent += "\nThe title is " + t
                    school_hour.title = t

                # Gets the location
                elif j == 'LOCATION':
                    t = str(i[j]).split(" ")
                    loc = []
                    for k in t:
                        if k not in loc:
                            loc.append(k)
                    loaction = ''
                    for k in loc:
                        loaction += k + " "
                    school_hour.location = crypting.encrypt(loaction[:-1], personal_password)

                # Gets the description of the hour
                elif j == 'DESCRIPTION':
                    school_hour.description = crypting.encrypt(str(i[j]), personal_password)

                # Gets what is needed for the hour
                elif j == 'RESOURCES':
                    school_hour.resources = crypting.encrypt(str(i[j]), personal_password)

                elif j not in ['UID', 'DTSTAMP', 'CATEGORIES']:
                    extra_text += str(i[j])

            # Makes all of the exclud hours
            # Makes a new excluded hour for every time it's excluded
            school_hour.extra = crypting.encrypt(extra_text, personal_password)
            school_hour.save()
            userRequest.user.profile.hours.add(school_hour)
            if hasExclude:
                for j in i['EXDATE'].dts:
                    extime = Exclude_schools_hours()
                    extime.school_hour = school_hour
                    extime.starttime = datetime.time(j.dt)
                    extime.date = datetime.date(j.dt)
                    extime.save()

    mailcontent += ("\nThere was " + str(new_hours) +
                    " created and " + str(old_hours) +
                    " where already in the system")

    # Sends a mail that lets me know how the schedule import whent
    sendMail(mailcontent,
             subject="New schedule",
             whoSent="Finite schedule import")

    # Lets the user know everthing is okej
    messages.success(userRequest, f'Your schedule has been successfully added')


def importIcsFile(file, userRequest):
    events = getEvents(file.read())
    school = Schools.objects.get_or_create(school_name="File import")[0]

    personal_password = hashing.strongHashing(userRequest.user.username,
                                              userRequest.user.date_joined)

    for event in events:
        school_hour = Schools_hours()
        school_hour.hourhash = "File import"
        school_hour.school = school
        for event_parts in event:
                # Gets the start time and date
                if event_parts == 'DTSTART':
                    school_hour.startdate = datetime.date(event[event_parts].dt)
                    school_hour.starttime = datetime.time(event[event_parts].dt)

                # Gets the end time and date
                elif event_parts == 'DTEND':
                    school_hour.endtime = datetime.time(event[event_parts].dt)
                    school_hour.enddate = datetime.date(event[event_parts].dt)

                                # If The event will run for many weeks
                elif event_parts == 'RRULE':
                    for rules in event[event_parts]:
                        for k in event[event_parts][rules]:
                            if rules == 'UNTIL':
                                # Updates the end date
                                school_hour.enddate = k
                            # The frequensy of the event happening
                            elif rules == 'FREQ':
                                # Need to add better frequensy
                                if k == 'WEEKLY':
                                    school_hour.frequense = 7
                                else:
                                    school_hour.frequense = 10

                # Gets the information like what lesson it is
                elif event_parts == 'SUMMARY':
                    school_hour.summary = crypting.encrypt(str(event[event_parts]), personal_password)
                    t = str(event[event_parts])
                    school_hour.title = t

                # Gets the description of the hour
                elif event_parts == 'DESCRIPTION':
                    school_hour.description = crypting.encrypt(str(event[event_parts]), personal_password)

        school_hour.save()
        userRequest.user.profile.hours.add(school_hour)

    # Lets the user know everthing is okej
    messages.success(userRequest, f'Your schedule has been successfully added')


# Gets the schedule from the the database
# The day is the varibel that you can change to get the schedule for t.ex. tomorrow
# The place argument is the one that spesifys if the set of hours is displayed in the first
# second or where ever on the schedule it should be displayed
def getScheduleForUser(user, day, place):
    datetoday = datetime.date(datetime.now() + timedelta(days=day, hours=-3))
    periods = []
    hours = Timmar.objects.filter(
        Q(user=user) & Q(startdate__lte=datetoday) &
        Q(enddate__gte=datetoday)
    )

    if user.profile.version == 2:
        hours = Schools_hours.objects.filter(
            Q(profile__user=user) &
            Q(startdate__lte=datetoday) &
            Q(enddate__gte=datetoday)
        )

    for j in hours:
        temp = {}
        if j.startdate <= datetoday <= j.enddate:
            if j.startdate == datetoday or j.enddate == datetoday:
                temp['start'] = str(j.starttime)[:5]
                temp['end'] = str(j.endtime)[:5]
                temp['title'] = j.title  # + " "+j.subjecttext.split(' ')[0]
            elif j.frequense == 0:
                continue
            else:
                startdate = j.startdate + timedelta(days=j.frequense)
                while True:
                    if startdate == datetoday:
                        temp['start'] = str(j.starttime)[:5]
                        temp['end'] = str(j.endtime)[:5]
                        temp[
                            'title'] = j.title  # + " "+j.subjecttext.split(' ')[0]
                        break
                    elif startdate > datetoday:
                        break
                    else:
                        startdate += timedelta(days=j.frequense)

            exclude = ExcludeTimmar.objects.filter(time=j.pk)
            if user.profile.version == 2:
                exclude = Exclude_schools_hours.objects.filter(school_hour__in=hours)
            if len(exclude) > 0:
                for i in exclude:
                    if i.date == datetoday and i.starttime == j.starttime:
                        temp = {}

        if len(temp) > 0:
            periods.append(temp)

    # To get correct data structure
    my = {'day': place, 'periods': periods}

    return my


# Gets the schedule for a user for the week that we are on right now
# Outputs the dictionary that is used in the html
def scheduleOutputWeek(user):
    # Gets the days that are in the week we are on
    datetoday = datetime.today() + timedelta(hours=3)
    datetoday = datetoday.weekday()
    days = []
    if datetoday == 5:
        for i in range(0, 7):
            days.append(i + 2)
    elif datetoday == 6:
        for i in range(0, 7):
            days.append(i + 1)
    else:
        for i in range(datetoday - datetoday * 2,
                       datetoday - datetoday * 2 + 7):
            days.append(i)

    output = {}
    count = 0
    # Gets the users schedule for the week
    week = [
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
        'Sunday'
    ]
    for i in days:
        output[week[count]] = [getScheduleForUser(user, i, count), i]
        count += 1

    return {'they': [[output]]}


# Gets the schedule for all users that is inputed in users
# Gets the schedule for a specific day that is inputed as a int
def scheduleOutputDay(users, day):
    count = 1
    sixPepole = []
    output = {'they': []}

    for user in users:
        # Gets the name of the user so it can be displayed
        name = Profile.objects.get(user_id=user.id)
        if name.realname != '' and name.importsuccess is True:
            realname = crypting.decrypt(name.realname,
                                        settings.CRYPTION_PASS_2)
            realclass = crypting.decrypt(name.realclass,
                                         settings.CRYPTION_PASS_2)
            displayname = str(
                realname.split(' ')[1] + ' ' + realname.split(' ')[0] +
                './' + realclass)
        else:
            displayname = name.user.get_username()

        sixPepole.append({
            displayname:
            [getScheduleForUser(user, day, count),
             name.user.get_username()]
        })

        count += 1
        if len(sixPepole) >= 6:
            count = 1
            output['they'].append(sixPepole)
            sixPepole = []

    if len(sixPepole) != 0:
        output['they'].append(sixPepole)
        sixPepole = []

    return output
