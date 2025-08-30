from rest_framework.routers import DefaultRouter
from rest_framework.urls import path
from . import views

app_name = 'inform'
router = DefaultRouter(trailing_slash=False)
router.register('inform', views.InformViewSet, basename='inform')

urlpatterns = [
    path('read',views.ReadInformView.as_view(), name='inform_read'),
] + router.urls
