from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from rest_framework import serializers

OAUser = get_user_model()


class AddStaffSerializer(serializers.Serializer):
    realname = serializers.CharField(max_length=20, min_length=2,
                                     error_messages={'required': '请输入用户名!',
                                                     'max_length': '最长不能超过20个字符',
                                                     'min_length': '最短不能少于2个字符'})
    email = serializers.EmailField(error_messages={'required': '请输入用户名!', 'invalid': '请输入正确格式的邮箱!'})
    password = serializers.CharField(max_length=20,
                                     error_messages={'required': '请输入密码!', 'max_length': '密码不能超过20个字符'})

    def validate(self, attrs):
        request = self.context.get('request')
        email = attrs.get('email')
        # 验证邮箱是否存在
        if OAUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('该邮箱已注册!')

        # 验证当前用户是否为部门的leader
        if request.user.department.leader_id != request.user.uid:
            raise serializers.ValidationError('非部门leader不能添加员工!')

        return attrs


class ActiveStaffSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages={'required': '请输入用户名!', 'invalid': '请输入正确格式的邮箱!'})
    password = serializers.CharField(max_length=20,
                                     error_messages={'required': '请输入密码!', 'max_length': '密码不能超过20个字符'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = OAUser.objects.filter(email=email).first()
        # 数据库中无该用户或者密码错误
        if not user or not user.check_password(password):
            raise serializers.ValidationError('邮箱或密码错误!')
        attrs['user'] = user
        return attrs


class StaffUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        error_messages={'required': "请先上传 '.xlsx' 或 '.xls' 文件!", }
    )
