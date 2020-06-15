from django.db import transaction

from rest_framework import serializers
from rest_framework.response import Response

from house.models import House
from order.models import Order


class OrderSerializers(serializers.ModelSerializer):
    house_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    ctime = serializers.DateTimeField(source='create_time', read_only=True)
    start_date = serializers.DateField(source='begin_date', read_only=True)
    img_url = serializers.CharField(source='house.index_image_url', read_only=True)
    order_id = serializers.CharField(source='id', read_only=True)
    status = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = ['user_id', 'house_id', 'begin_date', 'end_date', 'days', 'house_price', 'amount', 'comment', 'ctime',
                  'img_url', 'order_id', 'start_date', 'status', 'title']

    def create(self, validated_data):
        order = Order.objects.create(**validated_data)
        house = House.objects.get(id=order.house_id)
        if house.room_count == 0:
            return Response({'errno': '4001', 'errmsg': 'No room available'})
        house.order_count += 1
        house.save()
        return order
