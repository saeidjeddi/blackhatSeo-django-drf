from rest_framework import serializers
from .models import Proxy

class ProxySerializer(serializers.ModelSerializer):
    class Meta:
        model = Proxy
        fields = ['id', 'proxy_test', 'created_at']

