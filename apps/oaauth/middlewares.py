import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import exceptions, status
from rest_framework.authentication import get_authorization_header
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import reverse

OAUser = get_user_model()


class LoginCheckMiddleware(MiddlewareMixin):
    """
    针对除了 login 接口以外的所有接口都必须先进行登录后才可使用
    """
    keyword = 'JWT'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.white_list = [reverse("oaauth:login"),
                           reverse("staff:active_staff"),
                           reverse("home:health_check")]

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path in self.white_list or request.path.startswith(settings.MEDIA_URL):
            request.user = AnonymousUser()
            request.auth = None
            return None
        try:
            auth = get_authorization_header(request).split()

            if not auth or auth[0].lower() != self.keyword.lower().encode():
                raise exceptions.ValidationError('请传入JWT!')

            if len(auth) == 1:
                msg = 'Token验证失败!'
                raise exceptions.AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = 'Token验证失败'
                raise exceptions.AuthenticationFailed(msg)

            try:
                jwt_token = auth[1]
                # 在PyJWT(2.x及以上)版本, decode解码必须传递 algorithms 参数
                jwt_token_info = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = jwt_token_info.get('user_id')
                # 判断获取到的用户id是否存在
                try:
                    user = OAUser.objects.get(pk=user_id)
                    request.user = user
                    request.auth = jwt_token
                except:
                    msg = '用户不存在!'
                    raise exceptions.AuthenticationFailed(msg)
            except jwt.ExpiredSignatureError:
                msg = 'Token已经过期!'
                raise exceptions.AuthenticationFailed(msg)
        except Exception as e:
            msg = '请先登录!'
            return JsonResponse(data={"detail": msg}, status=status.HTTP_403_FORBIDDEN)
