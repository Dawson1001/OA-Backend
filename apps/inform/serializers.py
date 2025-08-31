from rest_framework import serializers
from .models import Inform, InformRead
from apps.oaauth.models import OADepartment
from apps.oaauth.serializers import UserSerializer, DepartmentSerializer


class InformReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformRead
        fields = '__all__'


class InformSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    departments = DepartmentSerializer(read_only=True, many=True)
    department_ids = serializers.ListField(min_length=0, write_only=True)
    reads = InformReadSerializer(read_only=True, many=True)

    # public = serializers.BooleanField(read_only=True)

    class Meta:
        model = Inform
        fields = '__all__'
        read_only_fields = ['public']

    def create(self, validated_data):
        request = self.context.get('request')
        department_ids = validated_data.pop('department_ids')
        department_ids = list(map(lambda value: int(value), department_ids))
        if 0 in department_ids:
            inform = Inform.objects.create(public=True, author=request.user, **validated_data)
        else:
            departments = OADepartment.objects.filter(id__in=department_ids)
            inform = Inform.objects.create(public=False, author=request.user, **validated_data)
            inform.departments.set(departments)
            inform.save()
        return inform


class ReadInformSerializer(serializers.Serializer):
    inform_pk = serializers.IntegerField(error_messages={'required': '请输入inform的id!'})