from django.urls import path
from . import views

app_name = 'home'


urlpatterns = [
    path('latest/inform',views.LatestInformView.as_view(), name='latest_inform'),
    path('latest/absent',views.LatestAbsenceView.as_view(), name='latest_absent'),
    path('department/staff/count',views.DepartmentStaffView.as_view(), name='department_staff_count'),
]