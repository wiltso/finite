from django.contrib.auth.models import User
from users.models import Profile
from django.utils.timezone import now


# Gets the some usefull data from the database about the days activity
def getStats() -> str:
    # Get the amount of users that have been on the site and how many has create an account
    usersActive = Profile.objects.filter(last_access=now()).count()
    joindUsers = Profile.objects.filter(date_joined=now()).count()

    # Gets the users that have been on the page today
    users = User.objects.filter(profile__accessamount__gt=0)

    # The mail text string
    usersAccess = "UsersStats:\n["

    # Get the amount of times the users have been on the page
    for user in users:
        usersAccess += "['" + str(user.id) + "','" + str(user.profile.accessamount) + "'],"
        user.profile.accessamount = 0
        user.save()

    # Removes the last , for easy import of the array
    usersAccess = usersAccess[:-1]

    # Adds the stats to the mail
    usersAccess += "]\nUserActiveToday:" + str(usersActive) + "\nUsersJoind:" + str(joindUsers)

    # returns the text for the mail
    return usersAccess
