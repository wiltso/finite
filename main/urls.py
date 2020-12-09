from django.urls import path, register_converter
from . import views

from schedule.converters import NegativeIntConverter
register_converter(NegativeIntConverter, 'negint')

urlpatterns = [
    path('', views.home, name='home'),
    path('front/page/', views.gotToFront, name='front'),
    path('<negint:day>/', views.listSchedules, name='schedule'),
    path('reporting/', views.sendReports, name="sendReports"),
]
