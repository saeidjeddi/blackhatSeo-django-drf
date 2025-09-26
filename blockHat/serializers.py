from time import time

from rest_framework import serializers
from .models import Proxy, TaskStatus

class ProxySerializer(serializers.ModelSerializer):
    class Meta:
        model = Proxy
        fields = ['id', 'proxy_test', 'created_at']

class UserAgentFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class ListHistoryTaskSerializer(serializers.ModelSerializer):
    processingTime = serializers.SerializerMethodField()

    class Meta:
        model = TaskStatus
        exclude = ['duration']

    def get_processingTime(self, obj):
        if obj.status == "RUNNING":
            seconds = int(time() - obj.created_at.timestamp())
        else:
            seconds = obj.duration

        if seconds is None:
            return None

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02}:{minutes:02}:{secs:02}"
