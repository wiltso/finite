from django.urls import path, register_converter
from . import views

from schedule.converters import NegativeIntConverter
register_converter(NegativeIntConverter, 'negint')

urlpatterns = [
    path('list/', views.Listgroups, name='listgroups'),

    path('groups/creat/', views.createGroup, name='groupscreat'),
    path('add/member/<str:group_name>/', views.addGroupMember, name='addGroupMember'),
    path('remove/member/<str:group_name>/', views.removeGroupMember, name='removeGroupsMember'),
    path('delete/<str:group_name>', views.deleteGroup, name='deletegroup'),

    path('see/<negint:day>/<str:group_name>/', views.seeGroup, name='seeGroup'),
]
