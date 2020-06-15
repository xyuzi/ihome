from rest_framework import serializers

from house.models import Area


class UserInfoSerializers(serializers.ModelSerializer):
    aid = serializers.CharField(source='id', read_only=True)
    aname = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = Area
        fields = ['aid', 'aname']
