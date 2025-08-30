from rest_framework import serializers, exceptions
from .models import AbsentType, Absence, AbsentStatusChoices
from .utils import get_responder
from apps.oaauth.serializers import UserSerializer


class AbsentTypeSerializer(serializers.ModelSerializer):
    # absences = 'AbsenceSerializer'(many=True, read_only=True)
    class Meta:
        model = AbsentType
        fields = '__all__'


class AbsenceSerializer(serializers.ModelSerializer):
    absent_type = AbsentTypeSerializer(read_only=True)
    absent_type_id = serializers.IntegerField(write_only=True)
    requester = UserSerializer(read_only=True)
    responder = UserSerializer(read_only=True)

    class Meta:
        model = Absence
        fields = '__all__'

    def validate_absent_type_id(self, value):
        if not AbsentType.objects.filter(pk=value).exists():
            raise exceptions.ValidationError(detail="请假类型不存在!")
        return value

    def create(self, validated_data):
        """ 申请请假 """
        request = self.context.get('request')
        user = request.user

        responder = get_responder(request)  # 获取审批人

        if responder is None:
            validated_data['status'] = AbsentStatusChoices.APPROVAL
        else:
            validated_data['status'] = AbsentStatusChoices.AUDITING
        return Absence.objects.post(**validated_data)

    def update(self, instance, validated_data):
        """ 审核请假 """
        if instance.status != AbsentStatusChoices.AUDITING:
            raise exceptions.APIException(detail="不能修改已经确定的请假数据!")

        user = self.context.get('request').user

        if instance.responder_id != user.uid:
            raise exceptions.AuthenticationFailed(detail="您无权处理该考勤!", )

        instance.status = validated_data.get("status")
        instance.responder_content = validated_data.get("responder_content")
        instance.save()
        return instance
