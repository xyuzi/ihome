from rest_framework import serializers

from house.models import House


class HousesSerializers(serializers.ModelSerializer):
    house_id = serializers.IntegerField(source='id')
    img_url = serializers.CharField(source='index_image_url')
    user_avatar = serializers.ImageField(source='user.avatar')
    area_name = serializers.CharField(source='area.name')
    ctime = serializers.DateTimeField(source='create_time')

    class Meta:
        model = House
        fields = ['address', 'area_name', 'house_id', 'img_url', 'order_count', 'price', 'room_count', 'title',
                  'user_avatar', 'ctime']
