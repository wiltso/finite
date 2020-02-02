from django.urls import path
from . import views

urlpatterns = [
    path('import/', views.importSchedule, name='importSchedule'),
    path('import/instruktions', views.importScheduleInstructions, name="wilmaLinkInstructions")
]
