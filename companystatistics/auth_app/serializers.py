from rest_framework import serializers

from .models import CSUser


class CSUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CSUser
        fields = ['id', 'username', 'first_name', 'email']
