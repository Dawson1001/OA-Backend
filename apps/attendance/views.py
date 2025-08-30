from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.oaauth.serializers import UserSerializer
from .models import Absence, AbsentType
from .serializers import AbsenceSerializer, AbsentTypeSerializer

from .utils import get_responder


# Create your views here.
# 1. 发起考勤（create）
# 2. 处理考勤（update）
# 3. 查看自己的考勤列表（list?who=my）
# 4. 查看下属的考勤列表（List?who=sub）

class AbsenceViewset(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer

    # 使用put方法进行部分修改
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        who = request.query_params.get('who')
        if who and who == 'sub':
            result = queryset.filter(responder=request.user)
        else:
            result = queryset.filter(requester=request.user)

        # 分页功能
        page = self.paginate_queryset(result)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(instance=result, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AbsentTypeView(APIView):
    """ 获取请假类型 """

    def get(self, request, *args, **kwargs):
        types = AbsentType.objects.all()
        serializer = AbsentTypeSerializer(instance=types, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ResponderView(APIView):
    """ 获取审批人 """

    def get(self, request, *args, **kwargs):
        responder = get_responder(request)
        serializer = UserSerializer(instance=responder)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
