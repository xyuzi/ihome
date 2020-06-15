import json
import re

from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection
from django.conf import settings
from fdfs_client.client import Fdfs_client

from rest_framework.response import Response
from rest_framework.views import APIView

from house.models import House
from ihome.libs.qiniuyun.qiniu_storage import storage
from ihome.utils.checkid import check
from user.models import User
from user.serializers.houses import HousesSerializers
from user.serializers.user import UserInfoSerializers


class Users(View):
    def post(self, request):
        dict = json.loads(request.body.decode())
        mobile = dict.get('mobile')
        phonecode = dict.get('phonecode')
        password = dict.get('password')
        password2 = dict.get('password2')

        if not all([mobile, phonecode, password, password2]):
            return JsonResponse({
                'errno': '4002',
                'errmsg': 'Required parameter missing'
            }, status=402)

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({
                'errno': '4002',
                'errmsg': 'Incorrect format of mobile number'
            }, status=402)

        if password2 != password:
            return JsonResponse({
                'errno': '4002',
                'errmsg': 'Two incorrect passwords'
            }, status=402)

        redis_conn = get_redis_connection('verify_code')
        phonecode_server = redis_conn.get('img_%s' % mobile)
        if not phonecode_server:
            return JsonResponse({
                'errno': '4002',
                'errmsg': 'Verification code expired'
            }, status=402)

        if phonecode != phonecode_server.decode():
            return JsonResponse({
                'errno': '4002',
                'errmsg': 'Incorrect verification code'
            }, status=402)
        redis_conn.delete('img_%s', mobile)
        try:
            try:
                User.objects.get(mobile=mobile)
                return JsonResponse({
                    'errno': '4002',
                    'errmsg': 'login has failed'
                })
            except:
                user = User.objects.create_user(username=mobile,
                                                mobile=mobile,
                                                password=password)
        except Exception as e:
            return JsonResponse({
                'errno': '4500',
                'errmsg': 'Save failed'
            }, status=402)
        login(user=user, request=request)
        return JsonResponse({
            "errno": '0',
            "errmsg": "login was successful"
        })


class UsersLogin(View):
    def post(self, request):
        dict = json.loads(request.body.decode())
        mobile = dict.get('mobile')
        password = dict.get('password')
        if not all([mobile, password]):
            return JsonResponse({
                'errno': '4102',
                'errmsg': 'Required parameter missing'
            }, status=402)
        user = authenticate(password=password, username=mobile)

        if not user:
            return JsonResponse({
                "errno": '0',
                "errmsg": "Wrong username or password"
            }, status=402)
        login(request, user)

        return JsonResponse({
            "errno": '0',
            "errmsg": "Login successful"
        })

    def get(self, request):

        """username右上角展示"""
        if request.user.is_authenticated:
            data = {
                'name': request.user.username,
                'user_id': request.user.id
            }
            return JsonResponse({
                "errno": '0',
                "errmsg": 'Logged in',
                'data': data
            })
        else:
            return JsonResponse({
                "errno": '4101',
                "errmsg": 'Not logged in'
            })

    def delete(self, request):
        logout(request)
        return JsonResponse({
            "errno": '0',
            "errmsg": 'Sign out'
        }, status=204)


class UserInfo(APIView):
    def get(self, request):
        user = request.user
        instance = UserInfoSerializers(user)
        try:
            data = instance.data
        except Exception as e:
            return Response({
                'errmsg': '4101',
                'errno': 'Not logged in'
            })
        return Response({
            'data': data,
            'errmsg': 'OK',
            'errno': '0'
        })


class UserInfoAvatar(View):
    def post(self, request):
        file = request.FILES.get('avatar')
        if not file:
            return JsonResponse({
                'errno': '4001',
                'errmsg': 'Required parameter missing'
            })
        client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        result = client.upload_by_buffer(file.read())
        if result.get('Status') != 'Upload successed.':
            raise Exception('上传文件到FDFS系统失败')
        url = result.get('Remote file_id')
        try:
            user = User.objects.get(id=request.user.id)
            user.avatar = url
            user.save()
        except Exception as e:
            return JsonResponse({
                'errno': '4101',
                'errmsg': 'Save failed'
            }, status=402)
        url = settings.FDFS_URL + url
        return JsonResponse({
            "data": {
                "avatar_url": url
            },
            "errno": "0",
            "errmsg": "Successfully uploaded the Avatar"
        }, status=201)


class UserInfoName(View):
    def put(self, request):
        name = json.loads(request.body.decode())
        id = request.user.id

        try:
            user = User.objects.get(id=id)
            user.username = name.get('name')
            user.save()
        except Exception as e:
            return JsonResponse({
                'errno': '4101',
                'errmsg': 'Save failed'
            })
        return JsonResponse({
            "errno": '0',
            "errmsg": 'Modification succeeded'
        }, status=201)


class UserInfoAuth(View):
    def post(self, request):
        dict = json.loads(request.body.decode())
        real_name = dict.get('real_name')
        id_card = dict.get('id_card')
        id = request.user.id
        if not check(id_card):
            return JsonResponse({
                'errno': '4001',
                'errmsg': 'ID card error'
            })
        try:
            User.objects.get(id_card=id_card)
            return JsonResponse({
                'errno': '4003',
                'errmsg': 'Duplicate ID card'
            })
        except:
            try:
                user = User.objects.get(id=id)
                user.real_name = real_name
                user.id_card = id_card
                user.save()
            except Exception as e:
                return JsonResponse({
                    'errno': '4101',
                    'errmsg': 'Save failed'
                })

            return JsonResponse({
                'errno': '0',
                'errmsg': 'Authentication information saved successfully',
                'data': {
                    'real_name': real_name,
                    'id_card': id_card
                }
            }, status=201)

    def get(self, request):
        try:
            id_card = request.user.id_card
            real_name = request.user.real_name
            if not all([id_card, real_name]):
                id_card = None
                real_name = None
            return JsonResponse({
                'errno': '0',
                'errmsg': 'ok',
                'data': {
                    'id_card': id_card,
                    'real_name': real_name
                }
            })
        except Exception as e:
            return JsonResponse({
                'errno': '0',
                'errmsg': 'none',
            })


class UserInfoHouses(APIView):
    def get(self, request):
        house = House.objects.filter(user_id=request.user.id).order_by('-create_time')
        instances = HousesSerializers(house, many=True)
        houses_list = []
        for instance in instances.data:
            instance['ctime'] = instance.get('ctime').split('T')[0]
            houses_list.append(instance)
        return Response({
            'errno': '0',
            'errmsg': 'ok',
            'data': {
                'houses': houses_list
            }
        })
