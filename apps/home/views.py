from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Prefetch, Count
from apps.inform.models import Inform, InformRead
from apps.inform.serializers import InformSerializer
from apps.attendance.models import Absence
from apps.attendance.serializers import AbsenceSerializer
from apps.oaauth.models import OADepartment
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


class LatestInformView(APIView):
    """
    返回最近10条通知: 公共通知 + 所在部门通知
    """

    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        current_user = request.user
        informs = Inform.objects.prefetch_related(
            Prefetch("reads", queryset=InformRead.objects.filter(reader_id=current_user.uid)), "departments").filter(
            Q(public=True) | Q(departments=current_user.department))[:10]
        serializer = InformSerializer(instance=informs, many=True)
        return Response(serializer.data)


class LatestAbsenceView(APIView):
    """
    返回最近十条请假信息: 董事会-->所有人 | 非董事会-->本部门内的请假信息
    """

    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        current_user = request.user
        queryset = Absence.objects
        if current_user.department.name != '董事会':
            queryset = queryset.filter(requester_id__department_id=current_user.department_id)
        serializer = AbsenceSerializer(instance=queryset.all().order_by('-create_time')[:10], many=True)
        return Response(serializer.data)


class DepartmentStaffView(APIView):
    """ 返回部门的员工数量信息 """

    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        results = OADepartment.objects.annotate(staff_count=Count('department_staffs')).values("name", "staff_count")
        return Response(results)


class HealthCheckView(APIView):
    """ API 健康检查 """

    def get(self, request):
        return Response(data={"status": "ok"}, status=status.HTTP_200_OK)
