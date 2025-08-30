from django.core.validators import FileExtensionValidator, get_available_image_extensions
from rest_framework import serializers


class UploadImageSerializer(serializers.Serializer):
    image = serializers.ImageField(
        validators=[FileExtensionValidator(get_available_image_extensions())],
        error_messages={"required": "请上传图片!", "invalid": "请上传正确的图片格式!"}
    )

    def validate_image(self, value):
        # 图片大小单位: KB
        max_size = 0.5 * 1024 * 1024  # 设置最大图片大小 0.5 MB
        size = value.size
        if size > max_size:
            raise serializers.ValidationError("图片最大不能超过0.5MB!")
        return value
