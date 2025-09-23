from rest_framework.views import APIView
from rest_framework.response import Response
from blockHat.models import TaskStatus
from time import time

class TaskStatusInfoApiView(APIView):
    def get(self, request, task_id):
        try:
            task_status = TaskStatus.objects.get(task_id=task_id)
        except TaskStatus.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

        duration = task_status.duration
        if task_status.status == "RUNNING":
            duration = time() - task_status.created_at.timestamp()

        return Response({
            "task_id": task_status.task_id,
            "url": task_status.url,
            "referer": task_status.referer,
            "status": task_status.status,
            "completed_requests": task_status.completed_requests,
            "request_granted": task_status.request_granted,
            "duration": int(duration)
        })
    