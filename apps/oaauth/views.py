from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import LoginSerializer, UserSerializer, ResetPasswordSerializer
from .authentications import generate_jwt
from datetime import datetime


# Create your views here.


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.last_login = datetime.now()
            user.save()
            token = generate_jwt(user)
            return Response({'token': token, 'user': UserSerializer(user).data})
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({"detail": detail, "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            password1 = serializer.validated_data.get('password1')
            request.user.set_password(password1)
            request.user.save()
            msg = "密码重置成功!"
            return Response(data={"detail": msg}, status=status.HTTP_200_OK)
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response(data={"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
