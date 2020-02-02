from django.urls import path
from . import views

urlpatterns = [
    path('listUser/', views.listAccountsSearch, name='searchForFriends'),
    path('listFriends/', views.listFriendsView, name='listfriends'),
    path('list/best/friends/', views.listBFFFriendsView, name='listBFFfriends'),
]
