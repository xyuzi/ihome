import datetime

from django.db.models import Q
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from fdfs_client.client import Fdfs_client
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.views import APIView

from house.models import Area, House, HouseImage
from house.serializers.area import UserInfoSerializers
from house.serializers.houses import HousesSerializer, HousesModelSerializer, HousesInfoModelSerializer
from house.serializers.index import HousesInfoSerializers
from user.models import User


class AreasView(APIView):
    def get(self, request):
        instance = UserInfoSerializers(Area.objects.all(), many=True)
        return Response({
            'errno': '0',
            'errmsg': 'Success',
            'data': instance.data
        })


class HousesView(CreateAPIView, ListAPIView):
    serializer_class = HousesSerializer

    def get_queryset(self):
        return User.objects.get(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        house = serializer.save()
        return Response({
            'errno': '0',
            'errmsg': 'ok',
            'data': {'house_id': house.id}
        })

    def list(self, request, *args, **kwargs):
        dict = request.GET
        aid = dict.get('aid') if dict.get('aid') else '1'
        sd = dict.get('sd') if dict.get('sd') else '2008-10-1'
        ed = dict.get('ed') if dict.get('ed') else '2008-10-2'
        sk = dict.get('sk') if dict.get('p') else 'new'
        p = dict.get('p') if dict.get('p') else 1
        sk_dict = {
            'new': 'create_time',
            'booking': 'order_count',
            'price-inc': 'price',
            'price-des': '-price'
        }

        try:
            start = datetime.datetime.strptime(sd, '%Y-%m-%d')
            end = datetime.datetime.strptime(ed, '%Y-%m-%d')
            result = abs((end - start).days)
        except:
            result = 1

        houses = House.objects.filter(
            (Q(area_id=aid) & Q(max_days=0) & Q(min_days__lte=result) & ~Q(room_count=0)) |
            (Q(area_id=aid) & Q(min_days__lte=result) & Q(max_days__gte=result) & ~Q(room_count=0))
        ).order_by(sk_dict.get(sk, 'new'))[(int(p) - 1) * 5:(int(p) - 1) * 5 + 5]

        serializer = HousesModelSerializer(houses, many=True)

        return Response({
            'data': {
                'houses': serializer.data,
                'total_page': p
            },
            'errmsg': 'OK',
            'errno': '0'
        })


class HousesImageView(View):
    def post(self, request, house_id):
        house = House.objects.get(id=house_id)
        client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        file = request.FILES.get('house_image')
        if not file:
            return JsonResponse({
                'errmsg': 'The lack of transport documents',
                'errno': '0'
            })
        result = client.upload_by_buffer(file.read())
        if result.get('Status') != 'Upload successed.':
            raise Exception('上传文件到FDFS系统失败')
        url = result.get('Remote file_id')
        url = settings.FDFS_URL + url
        if not house.index_image_url:
            house.index_image_url = url
            house.save()
            HouseImage.objects.create(house_id=house_id,
                                      url=url)
        else:
            HouseImage.objects.create(house_id=house_id,
                                      url=url)
        return JsonResponse({
            "data": {
                "url": url
            },
            "errno": "0",
            "errmsg": "Picture uploaded successfully"
        })


class HousesIndexView(APIView):
    def get(self, request):
        houses = House.objects.filter(~Q(room_count=0)).order_by('-create_time')[:5]
        instance = HousesInfoSerializers(houses, many=True)
        return Response({
            'data': instance.data,
            'errno': '0',
            'errmsg': 'OK'
        })


class HousesInfoView(RetrieveAPIView):
    queryset = House.objects.all()
    serializer_class = HousesInfoModelSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        for index, ctime in enumerate(serializer.data.get('comments')):
            serializer.data['comments'][index]['ctime'] = ctime.get('ctime').split('T')[0]
        return Response({
            'data': {
                'house': serializer.data,
                'user_id': -1 if self.request.user is None else self.request.user.id
            },
            'errno': '0',
            'errmsg': 'OK'
        })
