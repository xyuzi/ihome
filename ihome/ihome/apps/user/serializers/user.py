from rest_framework import serializers

from user.models import User


class UserInfoSerializers(serializers.ModelSerializer):
    name = serializers.CharField(source='username', read_only=True)
    user_id = serializers.CharField(source='id', read_only=True)
    create_time = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = ['avatar', 'create_time', 'mobile', 'name', 'user_id']
