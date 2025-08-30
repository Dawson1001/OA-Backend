from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UploadImageSerializer
from shortuuid import uuid
import os
from django.conf import settings


# Create your views here.

class UploadImageView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UploadImageSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data.get("image")
            filename = uuid() + os.path.splitext(file.name)[-1]
            path = settings.MEDIA_ROOT / filename
            try:
                with open(path, "wb") as f:
                    for chunk in file.chunks():
                        f.write(chunk)
            except Exception:
                return Response(data={
                    "errno": 1,
                    "message": "图片保存失败!"
                })

            file_url = settings.MEDIA_URL + filename
            return Response(data={
                "errno": 0,
                "data": {
                    "url": file_url,  # 图片src，必须
                    "alt": "yyy",  # 图片描述文字，非必须
                    "href": file_url  # 图片的链接，非必须
                }
            })

        else:
            # print(serializer.errors)
            return Response(data={
                "errno": 1,
                "message": list(serializer.errors.values())[0][0]
            })
