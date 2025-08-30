from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Inform, InformRead
from .serializers import InformSerializer, ReadInformSerializer
from django.db.models import Q
from django.db.models import Prefetch


# Create your views here.

class InformViewSet(viewsets.ModelViewSet):
    queryset = Inform.objects.all()
    serializer_class = InformSerializer

    def get_queryset(self):
        """
        通知列表:
        1. inform.public=True
        2. inform.departments包含了用户所在的部门
        3. inform.author = request.user
        """
        # select_related : 在提取某个模型的数据的同时, 也提前将相关联的数据提取出来
        # 但只能用在 '一对多' 或者 '一对一' 中
        queryset = self.queryset.select_related('author').prefetch_related(
            Prefetch("reads", queryset=InformRead.objects.filter(reader_id=self.request.user.uid)), 'departments').filter(
            Q(public=True) | Q(departments=self.request.user.department) | Q(author=self.request.user)).distinct()
        # for inform in queryset:
        #     inform.is_read = InformRead.objects.filter(inform=inform, reader=self.request.user).exsits()
        # 性能差, 需要多次执行SQL语句
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author.uid == self.request.user.uid:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['read_count'] = InformRead.objects.filter(inform_id=instance.id).count()
        return Response(data=data)


class ReadInformView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ReadInformSerializer(data=request.data)
        if serializer.is_valid():
            inform_pk = serializer.data.get('inform_pk')
            if InformRead.objects.filter(inform_id=inform_pk, reader_id=request.user.uid).exists():
                return Response(status=status.HTTP_200_OK)
            else:
                try:
                    InformRead.objects.post()
                except Exception as e:
                    print(e)
                    return Response(data={'detail': '阅读失败!'}, status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_200_OK)
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response(data={'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
