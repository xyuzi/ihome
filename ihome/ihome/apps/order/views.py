import datetime
import json

from django.db.models import Q
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from house.models import House
from order.models import Order
from order.serializers.order import OrderSerializers


class OrdersView(CreateAPIView, ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializers

    def create(self, request, *args, **kwargs):
        dict = self.request.data
        start_date = dict.get('start_date')
        end_date = dict.get('end_date')
        house_id = dict.get('house_id')
        try:
            start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            result = (end - start).days
            house = House.objects.get(
                (Q(id=house_id) & ~Q(user=self.request.user) & Q(max_days=0) & Q(min_days__lte=result)) |
                (Q(id=house_id) & ~Q(user=self.request.user) & Q(min_days__lte=result) & Q(max_days__gte=result))
            )
        except Exception as e:
            return Response({
                'errno': '4001',
                'errmsg': 'Invalid data. \n'
                          'Please check whether the order date matches\n'
                          "You can't order your own room"
            })
        user_id = self.request.user.id
        try:
            Order.objects.get(house_id=house_id, user_id=user_id, status__in=[0, 1, 2, 3, 4])
            return Response({
                'errno': '4001',
                'errmsg': 'You have reserved this room'
            })
        except:
            data = {
                'user_id': user_id,
                'house_id': house_id,
                'begin_date': start_date,
                'end_date': end_date,
                'days': result,
                'house_price': house.price,
                'amount': int(house.price) * result
            }
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            order = serializer.save()
            return Response({
                'data': {
                    'order_id': order.id
                },
                'errno': '0',
                'errmsg': 'OK'
            }, status=201)

    def list(self, request, *args, **kwargs):
        role = self.request.GET.get('role')

        order = Order.objects.filter(user_id=self.request.user.id).order_by('-create_time') if role == 'custom' else Order.objects.filter(
            house_id__in=[house.id for house in House.objects.filter(user_id=request.user.id)]).order_by('-create_time')
        serializers = self.serializer_class(order, many=True)
        orders = []
        for serializer in serializers.data:
            serializer['status'] = Order.ORDER_STATUS_ENUM.get(int(serializer['status']))
            serializer['ctime'] = serializer.get('ctime').split('T')[0]
            orders.append(serializer)
        return Response({
            'data': {
                'orders': orders
            },
            'errno': '0',
            'errmsg': 'OK'
        })


class OrdersStatusView(APIView):

    def put(self, request, pk):
        order = Order.objects.get(Q(id=pk) & Q(status=0))
        action = json.loads(request.body.decode())
        if action.get('action') == 'accept':
            order.status = Order.ORDER_STATUS['WAIT_COMMENT']
            house = House.objects.get(id=order.house_id)
            if house.room_count == 0:
                return Response({'errno': '4001', 'errmsg': 'No room available'})
            house.room_count -= 1
            house.save()
        else:
            order.status = Order.ORDER_STATUS['REJECTED']
            house = House.objects.get(id=order.house_id)
            house.order_count -= 1
            house.save()
        order.comment = action.get('reason')
        order.save()
        return Response({
            'errno': '0',
            'errmsg': 'operate successfully'
        })


class OrdersCommentView(APIView):

    def put(self, request, pk):
        order = Order.objects.get(Q(id=pk) & Q(status=3))
        order.comment = json.loads(request.body.decode()).get('comment')
        order.status = Order.ORDER_STATUS['COMPLETE']
        order.save()
        return Response({
            'errno': '0',
            'errmsg': 'Comment on success'
        })
