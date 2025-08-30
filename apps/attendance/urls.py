from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.attendance import views


app_name = 'attendance'

router = DefaultRouter(trailing_slash=False)
# https://domain/absent/absent
router.register('absent', views.AbsenceViewset, basename='absent')

urlpatterns = [
    path('type', views.AbsentTypeView.as_view(), name='absenttypes'),
    path('responder', views.ResponderView.as_view(), name='getresponder'),
] + router.urls
