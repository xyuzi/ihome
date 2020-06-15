from rest_framework import serializers

from house.models import House, HouseImage, Facility
from order.models import Order


class HousesSerializer(serializers.ModelSerializer):
    area_id = serializers.IntegerField()
    house_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = House
        fields = ['acreage', 'address', 'area_id', 'beds', 'capacity', 'deposit', 'facility', 'max_days', 'min_days',
                  'price', 'room_count', 'title', 'unit', 'user_id', 'house_id']

    def create(self, validated_data):
        facilitys = validated_data.pop('facility')
        house = House.objects.create(user_id=self.context.get('request').user.id, **validated_data)
        house.facility.add(*facilitys)
        return house


class HousesModelSerializer(serializers.ModelSerializer):
    area_name = serializers.StringRelatedField()
    user_avatar = serializers.ImageField(source='user.avatar')
    ctime = serializers.DateTimeField(source='create_time')
    house_id = serializers.CharField(source='id')
    img_url = serializers.CharField(source='index_image_url')

    class Meta:
        model = House
        fields = ['address', 'area_name', 'ctime', 'house_id', 'img_url', 'order_count', 'price', 'room_count', 'title',
                  'user_avatar']


class CommentsSerializer(serializers.ModelSerializer):
    ctime = serializers.DateTimeField(source='create_time')
    user_name = serializers.StringRelatedField(source='user.username')

    class Meta:
        model = Order
        fields = ['comment', 'ctime', 'user_name']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseImage
        fields = ['url']


class HousesInfoModelSerializer(serializers.ModelSerializer):
    comments = CommentsSerializer(source='orders', many=True)
    hid = serializers.CharField(source='id')
    # img_urls = ImageSerializer(source='url', many=True)
    img_urls = serializers.StringRelatedField(many=True)
    user_avatar = serializers.ImageField(source='user.avatar')
    user_id = serializers.PrimaryKeyRelatedField(read_only=True)
    user_name = serializers.CharField(source='user.username')
    facilities = serializers.PrimaryKeyRelatedField(source='facility', read_only=True, many=True)

    class Meta:
        model = House
        fields = ['acreage', 'address', 'beds', 'capacity', 'comments', 'deposit', 'facilities', 'hid', 'img_urls',
                  'max_days', 'min_days', 'price', 'room_count', 'title', 'unit', 'user_avatar', 'user_id', 'user_name']
