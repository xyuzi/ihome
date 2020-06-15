import re

from django.contrib.auth.backends import ModelBackend
from django.http import JsonResponse

from user.models import User


def get_mobile(username):
    try:
        # 正则判断手机号是否正确
        if re.match(r'^1[3-9]\d{9}', username):
            # User数据库查找 这里username 实际上使传入进来的mobile
            user = User.objects.get(mobile=username)
        else:
            # 手机号格式不正确
            return None
    except Exception as e:
        # 数据库查找失败
        return None
    else:
        # 将重新查找到的user返回
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """重写authenticate"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_mobile(username)
        # 进行check_password判断密码是否正确
        if user and user.check_password(password):
            return user
