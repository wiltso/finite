from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from friendship.models import Friendship
from django.shortcuts import render
from django.db.models import Q, Case, When
from users.models import Profile


# The base query that sorts users in the correct order
# Excludes test accounts (they use my email adress)
# Also excludes the users that made the request
# It's fine to do it like this becouse python is so laysi that it won't make the query
# to the db here
# It will make the query in the template first
def baseQuery(request):
    return User.objects.exclude(email='wilindho@gmail.com').exclude(
                username=request.user.username).distinct().order_by(
                    Case(When(profile__school=request.user.profile.school, then=2)),
                    Case(When(profile__age=request.user.profile.age, then=1)), 'username')


def makeQuerry(request, query, age, school):
    users = baseQuery(request)

    if query:
        users = users.filter(username__icontains=query)

    if age and school:
        users = users.filter(Q(profile__age=request.user.profile.age) &
                             Q(profile__school=request.user.profile.school))

    elif age:
        users = users.filter(profile__age=request.user.profile.age)

    elif school:
        users = users.filter(profile__school=request.user.profile.school)

    return users


# This is the view for the search users view
@login_required
def listAccountsSearch(request, moreMessages=None):
    # Needs to be false if there is no search for a username
    query = False
    # Needs to check if there is text in the search arg
    # Else it query would become None insted of False and would fail further down
    if request.GET.get('search'):
        query = str(request.GET.get('search'))

    # School and age you can do it directly becouse if there is not that args it will be False
    age = bool(request.GET.get('age'))
    school = bool(request.GET.get('school'))

    # Message needs to be global in the function
    messageToUser = False

    users = makeQuerry(request, query, age, school)

    # Sets the messages that are displayed if you make a query that has no results
    # The messageToUser array might look a wierd here but it's made this way to make
    # The html template more clear
    if query:
        if not users:
            messageToUser = ["Typo?", ["We are sorry to inform you that",
                                       "this username does not exist!"]]

    elif age and school:
        if not users:
            messageToUser = ["Oops!", ["Nobody from your school who's",
                                       "in the same grade as you",
                                       "is using Finite",
                                       "",
                                       "Spread Finite to your friends!"]]

    elif age:
        if not users:
            messageToUser = ["Oops", ["Nobody from your grade is using Finite",
                                      "",
                                      "Spread Finite to your friends!"]]

    elif school:
        if not users:
            messageToUser = ["Oops!", ["Nobody from your school is using Finite",
                                       "",
                                       "Spread Finite to your friends!"]]

    else:
        # Removes the accounts that have the pivate setting on
        # This is reversed due to updates and that we hade users when this was implemented
        # TODO: Reverse the private setting
        users = users.exclude(settings__private=True)
        messageToUser = ["Search for your friends", ["Type your friends username",
                                                     "into the search field",
                                                     " and press \"Search\""]]

    # Makes sure that you don't make a huge query for all users
    if len(users) > 50:
        users = users[:50]

    # TODO: Way is this here
    if moreMessages:
        for message in moreMessages:
            messageToUser.append(message)

    tohtml = {
        'users': users,
        'messagesToUser': messageToUser,
        'title': "Search users",
        'sender': 'searchForFriends'
    }

    return render(request, 'friendship/searchfriends.html', tohtml)


# This is the view that loads when you go to my friends
# Or if you make a query there and your last query returnd with one or more users
@login_required
def listFriendsView(request):
    # Needs to be false if there is no search for a username
    query = False
    # Needs to check if there is text in the search arg
    # Else it query would become None insted of False and would fail further down
    if request.GET.get('search'):
        query = str(request.GET.get('search'))

    # School and age you can do it directly becouse if there is not that args it will be False
    age = bool(request.GET.get('age'))
    school = bool(request.GET.get('school'))

    # Message needs to be global in the function
    messageToUser = False

    # The sender is for the template to know where to make the query if some one make a new query
    # This is so if you have no friend you can make a new query and find friends
    sender = "listfriends"

    users = makeQuerry(request, query, age, school)

    # filters away all of the users that is not a firend with the requesting person
    users = users.filter(
        Q(user__in=Friendship.objects.filter(friend_id=request.user.id).exclude(pending=True)) |
        Q(friend__in=Friendship.objects.filter(user_id=request.user.id).exclude(pending=True))
    )

    # Sets the messages that are displayed if you make a query that has no results
    # The messageToUser array might look a wierd here but it's made this way to make
    # The html template more clear
    if query:
        if not users:
            messageToUser = ["Typo?", ["None of your friends have that username!"]]

    elif age and school:
        if not users:
            messageToUser = ["Oops!", ["You have no friends from",
                                       "your school who are in",
                                       "the same grade as you!",
                                       "",
                                       "Spread Finite to them friends!"]]

    elif age:
        if not users:
            messageToUser = ["Oops!", ["You have no friends from the same grade!",
                                       "",
                                       "Spread Finite to your friends!"]]

    elif school:
        if not users:
            messageToUser = ["Oops!", ["You have no friends from your school!",
                                       "",
                                       "Spread Finite to your friends!"]]

    if not users:
        messageToUser = [
            "Friends?", ["It appears that you have no friends!",
                         "Use the search field above to find them!"]
        ]
        sender = 'searchForFriends'

    tohtml = {
        'users': users,
        'messagesToUser': messageToUser,
        'title': "My friends",
        'sender': sender
    }

    return render(request, 'friendship/searchfriends.html', tohtml)


# This loads if you go to my best friends
@login_required
def listBFFFriendsView(request):
    messageToUser = False

    # Gets all of the your BFFs users id
    myBFFs = Profile.objects.get(user_id=request.user.id).bff.all()
    # Gets all of thos users User object
    users = list(map(lambda x: User.objects.get(id=x.id), myBFFs))

    # If you don't have any friends this message will show
    if not users:
        messageToUser = [
            'Missing best friends?',
            ["We are sorry to inform you that you currently have no best friends"],
            "How do i get best friends?",
            ["You can categorise someones friendship status on their profile!"]
        ]

    tohtml = {
        'users': users,
        'messagesToUser': messageToUser,
        'title': "My best friends"
    }

    return render(request, 'friendship/searchfriends.html', tohtml)
