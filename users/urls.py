from django.contrib.auth import views as auth_views
from django.urls import path, register_converter
from . import views

from schedule.converters import NegativeIntConverter
register_converter(NegativeIntConverter, 'negint')

urlpatterns = [
      path('register/', views.register, name='register'),
      path('terms/conditions', views.termsConditions, name='Terms'),

      path(
            'login/',
            auth_views.LoginView.as_view(template_name='users/login.html'),
            name='login'),
      path(
            'logout/',
            auth_views.LogoutView.as_view(template_name='users/logout.html'),
            name='logout'),

      path(
            'password-reset/',
            auth_views.PasswordResetView.as_view(template_name='users/resetPassword.html'),
            name='password_reset'),
      path(
            'password-reset/done/',
            auth_views.PasswordResetDoneView.as_view(template_name='users/resetPasswordDone.html'),
            name='password_reset_done'),
      path(
            'password-reset-confirm/<uidb64>/<token>/',
            auth_views.PasswordResetConfirmView.as_view(template_name='users/resetPasswordConfirm.html'),
            name='password_reset_confirm'),
      path(
            'password-reset-complete/',
            views.afterPasswordReset,
            name='password_reset_complete'),

      path('profile/', views.profile, name='profile'),
      path('usersetting/', views.settings, name='settings'),
      path('user/changepassword/', views.changePassword, name='changePassword'),

      path('view/profile/<str:username>/', views.seeProfile, name='seeprofile'),
      path(
            'view/profile/<str:username>/<negint:day>/',
            views.compareSchedules,
            name='compareSchedule'),

      path('friend/request/<str:username>/', views.addFriend, name='addFriendRequest'),
      path('remove/friendship/<str:username>/', views.removeFriend, name='removeFriend'),

      path(
            'friend/request/accepted/<int:pk>/',
            views.acceptFriendRequest,
            name='friendRequestAccept'),
      path(
            'friend/request/reject/<int:pk>/',
            views.rejectFriendRequest,
            name='friendRequestReject'),

      path('newTerms/', views.newTearms, name='newTermsAccepted'),
      path('accepted/newterms/', views.acceptedNewTearms, name='acceptedTearms'),

]
