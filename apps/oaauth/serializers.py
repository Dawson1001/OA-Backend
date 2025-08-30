from rest_framework import serializers

from .models import OAUser, UserStatusChoices, OADepartment


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, error_messages={"required": "请输入邮箱!"})
    password = serializers.CharField(max_length=20, min_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = OAUser.objects.filter(email=email).first()
            # 验证邮箱用户存在与否
            if not user:
                raise serializers.ValidationError("该邮箱未注册!")
            # 验证用户密码
            if not user.check_password(password):
                raise serializers.ValidationError("密码错误! 请输入正确的密码!")
            # 验证用户状态
            if user.status == UserStatusChoices.UNACTIVE:
                raise serializers.ValidationError("该用户尚未激活!")
            elif user.status == UserStatusChoices.LOCKED:
                raise serializers.ValidationError("该用户已被锁定, 请联系管理员!")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("请输入邮箱和密码!")
        return attrs


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OADepartment
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()

    class Meta:
        model = OAUser
        exclude = ('password', 'groups', 'user_permissions')


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=20, min_length=6,
                                         error_messages={"required": "此字段必传!"})
    password1 = serializers.CharField(max_length=20, min_length=6,
                                      error_messages={"required": "此字段必传!", "max_length": "密码最长为20位",
                                                      "min_length": "密码最短为6位"})
    password2 = serializers.CharField(max_length=20, min_length=6,
                                      error_messages={"required": "此字段必传!"})

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')
        user = self.context.get("request").user

        if not user.check_password(old_password):
            raise serializers.ValidationError("旧密码错误!")

        if password1 != password2:
            raise serializers.ValidationError("新密码不一致!")

        return attrs
