import jwt
import time
from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header, TokenAuthentication
from .models import OAUser


def generate_jwt(user):
    timestamp = int(time.time()) + 60 * 60 * 24 * 7  # 单位: 秒
    # timestamp = int(time.time()) + 2  # 测试token过期
    # 因为jwt.encode返回的是bytes数据类型,  因此需要decode解码成str数据类型
    # 在PyJWT(2.x及以上)，jwt.encode()返回的已经是字符串(str)，不再是bytes。不需要再decode，直接用即可
    return jwt.encode({"user_id": user.pk, "exp": timestamp}, settings.SECRET_KEY)


class UserTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        # from rest_framework.request import Request
        # 这里的request对象是DRF自己的, 区别于django中自带的request
        # 需要从 django 自带的 request 提取给 DRF 中的_request
        return request._request.user, request._request.auth


class JwtAuthentication(BaseAuthentication):
    """
    Authorization: JWT XXXXXX...X
    """

    keyword = 'JWT'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

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
                return user, jwt_token
            except:
                msg = '用户不存在!'
                raise exceptions.AuthenticationFailed(msg)
        except jwt.ExpiredSignatureError:
            msg = 'Token已经过期!'
            raise exceptions.AuthenticationFailed(msg)
