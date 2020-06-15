from rest_framework import serializers

from house.models import House


class HousesInfoSerializers(serializers.ModelSerializer):
    house_id = serializers.CharField(source='id')
    img_url = serializers.CharField(source='index_image_url')
    class Meta:
        model = House
        fields = ['house_id', 'img_url', 'title']