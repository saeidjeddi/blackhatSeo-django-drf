from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import TaskStatus
from ..serializers import ListHistoryTaskSerializer




class ListHistoryTaskStatusView(APIView):
    serializer_class = ListHistoryTaskSerializer
    def get(self, request):
        tasks = TaskStatus.objects.all().order_by('-status', '-updated_at')
        serializer = ListHistoryTaskSerializer(tasks, many=True)
        return Response(serializer.data)
