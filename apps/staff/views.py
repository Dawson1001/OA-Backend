from django.http import JsonResponse
from django.shortcuts import render
from urllib import parse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics, exceptions, viewsets, mixins
from apps.oaauth.models import OADepartment, UserStatusChoices
from apps.oaauth.serializers import DepartmentSerializer, UserSerializer
from .serializers import AddStaffSerializer, ActiveStaffSerializer, StaffUploadSerializer
from django.contrib.auth import get_user_model
from django.views import View
from django.conf import settings
from utils import aeser
from django.urls import reverse
from oaback.celery import debug_task
from .tasks import send_mail_task
from .paginations import StaffListPagination
from datetime import datetime
import json
import pandas as pd
from django.http import HttpResponse
from django.db import transaction

OAUser = get_user_model()
aes = aeser.AESCipher(settings.SECRET_KEY)


def send_active_mail(request, email):
    """
    发送一个链接, 让用户点击这个链接后, 跳转到激活页面, 完成账号激活
    为了区分用户链接, 在发送链接邮件中包含该用户的邮箱
    邮箱加密算法: AES
    """
    token = aes.encrypt(email)
    # /staff/active?token=xxx
    active_path = reverse('staff:active_staff') + '?' + parse.urlencode({'token': token})
    active_url = request.build_absolute_uri(active_path)
    message = f'请点击以下链接激活账号,{active_url}'
    # send_mail("【XX企业】账号激活", message=message,recipient_list=[email], from_email=settings.DEFAULT_FROM_EMAIL)
    # 采用celery异步发送邮件
    send_mail_task.delay(email, message)


# Create your views here.

class DepartmentListView(generics.ListAPIView):
    queryset = OADepartment.objects.all()
    serializer_class = DepartmentSerializer


class ActiveStaffView(View):
    """
    员工账号激活过程:
    1. 新员工访问激活链接, 进入激活页面, 在进入页面前把链接中的token值存在cookie中, token值是新员工邮箱的AES加密值
    2. 新员工提交邮箱与初始密码, 后台验证解密后token的邮箱是否与新员工的邮箱一致, 一致则激活成功
    """

    def get(self, request):
        token = request.GET.get('token')
        response = render(request, 'active.html')
        response.set_cookie('token', token)
        return response

    # @method_decorator(csrf_protect, name="dispatch")
    def post(self, request):
        try:
            token = request.COOKIES['token']
            email = aes.decrypt(token)
            serializer = ActiveStaffSerializer(data=request.POST)
            if serializer.is_valid():
                form_email = serializer.validated_data.get('email')
                user = serializer.validated_data.get('user')
                if form_email != email:
                    return JsonResponse({'code': '400', 'message': '邮箱错误!'})
                user.status = UserStatusChoices.ACTIVED
                user.save()
                return JsonResponse({'code': '200', 'message': '账号激活成功!'})
            else:
                return JsonResponse({'code': 400, 'message': list(serializer.errors.values())[0][0]})
        except Exception as e:
            return JsonResponse({'code': 400, 'message': 'token错误!'})


class StaffViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin):
    queryset = OAUser.objects.all()
    pagination_class = StaffListPagination

    def get_serializer_class(self):
        if self.request.method in ['GET', 'PUT']:
            return UserSerializer
        else:
            return AddStaffSerializer

    def get_queryset(self):
        """
        获取员工列表:
        1. 如果是董事会, 返回所有员工
        2. 如果不是董事会, 但是是部门leader, 返回该部门的员工
        3. 如果不是上述二者, 返回 403_FORBIDDEN 错误
        """
        department_id = self.request.query_params.get('department_id')
        realname = self.request.query_params.get('realname')
        date_joined = self.request.query_params.getlist('date_joined[]')

        queryset = self.queryset
        user = self.request.user
        if user.department.name != '董事会':
            if user.department.leader_id != user.uid:
                raise exceptions.PermissionDenied()
            else:
                queryset = queryset.filter(department_id=user.department_id)
        else:
            if department_id:
                queryset = queryset.filter(department_id=department_id)
        if realname:
            queryset = queryset.filter(real_name__icontains=realname)
        if date_joined:
            try:
                start_date = datetime.strptime(date_joined[0], '%Y-%m-%d')
                end_date = datetime.strptime(date_joined[1], '%Y-%m-%d')
                queryset = queryset.filter(date_joined__range=(start_date, end_date))
            except Exception:
                pass
        return queryset.order_by('date_joined').all()

    def create(self, request, *args, **kwargs):
        """ 新增部门员工 """
        # 使用视图集的话, request会自己保存在context中
        # 直接继承APIView的话, 需要手动把request添加到context中
        serializer = AddStaffSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            realname = serializer.validated_data.get('realname')
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            # 保存新用户数据
            user = OAUser.objects.create_user(real_name=realname, email=email, password=password)
            user.department = request.user.department
            user.save()

            # 发送新用户激活邮件
            send_active_mail(request, email)

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(data={'detail': list(serializer.errors.values())[0][0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class StaffDownloadView(APIView):
    """ 下载员工信息 """

    def get(self, request):
        """
        /staff/download?pks=[id1, id2, ...]
        ['id1', 'id2', ...] --> JSON格式
        """
        try:
            pks = request.query_params.get('pks')
            try:
                pks = json.loads(pks)
            except Exception:
                return Response({'detail': '员工参数错误!'}, status=status.HTTP_400_BAD_REQUEST)
            current_user = request.user
            queryset = OAUser.objects.all()
            if current_user.department.name != '董事会':
                # 如果是普通员工操作
                if current_user.department.leader_id != current_user.uid:
                    return Response(data={'detail': '您没有下载权限'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    # 如果是部门leader, 先过滤为本部门的员工
                    queryset = queryset.filter(department_id=current_user.department_id)
            queryset = queryset.filter(pk__in=pks)
            result = queryset.values("real_name", "email", "department__name", "date_joined", "status")
            staff_df = pd.DataFrame(list(result))
            staff_df = staff_df.rename(
                columns={'real_name': '姓名', 'email': '邮箱', "department__name": "部门", "date_joined": "入职日期",
                         'status': '账号状态'})
            response = HttpResponse(
                content_type="application/xlsx",
                headers={"Content-Disposition": 'attachment; filename="员工信息.xlsx"'},
            )
            with pd.ExcelWriter(response) as writer:
                staff_df.to_excel(writer, sheet_name='员工信息', index=False)
            return response
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StaffUploadView(APIView):
    """ 上传员工信息 """

    def post(self, request):
        serializer = StaffUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data.get('file')
            # 如果是董事会 or 部门leader 才能权限进行上传
            current_user = request.user
            if current_user.department.name != '董事会' or current_user.department.leader_id != current_user.uid:
                return Response(data={'detail': '您没有上传权限!'}, status=status.HTTP_403_FORBIDDEN)

            staff_df = pd.read_excel(file)
            users = []
            for index, row in staff_df.iterrows():
                # 获取部门
                if current_user.department.name != '董事会':
                    department = current_user.department
                else:
                    try:
                        department = OADepartment.objects.filter(name=row['部门']).first()
                        if not department:
                            return Response(data={'detail': f"{row['部门']}不存在!"},
                                            status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        return Response(data={'detail': "部门列不存在!"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    email = row['邮箱']
                    real_name = row['姓名']
                    password = "111111"

                    user = OAUser(email=email, real_name=real_name, department=department, status=UserStatusChoices.UNACTIVE)
                    user.set_password(password)
                    users.append(user)
                except Exception:
                    return Response(data={'detail': "请检查文件中的邮箱、姓名以及部门名称!"}, status=status.HTTP_400_BAD_REQUEST)
            # 创建事务, 确保全部添加进数据库
            try:
                with transaction.atomic():
                    OAUser.objects.bulk_create(users)
            except Exception:
                return Response(data={'detail': "员工数据添加失败!"}, status=status.HTTP_400_BAD_REQUEST)

            # 异步为每一位新员工发送激活邮件
            for user in users:
                send_active_mail(request, user.email)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(data={'detail': list(serializer.errors.values())[0][0]}, status=status.HTTP_400_BAD_REQUEST)


class CeleryTestView(APIView):
    """ 测试celery """

    def get(self, request):
        debug_task.delay()
        return Response(data={'detail': 'start successfully!'})
