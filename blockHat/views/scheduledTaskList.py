from rest_framework.views import APIView
from rest_framework.response import Response
from celery import current_app
from ..models import TaskStatus
from rest_framework.permissions import IsAuthenticated
from accounts.jwtAuth import JWTAuthentication

class ScheduledTaskListApiView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    def get(self, request):
        tasks = TaskStatus.objects.filter(status="PENDING").order_by("-created_at")
        data = [
            {
                "user": request.user.username,
                "task_id": t.task_id,
                "url": t.url,
                "status": t.status,
                "eta": t.eta,
                "created_at": t.created_at
            }
            for t in tasks
        ]
        return Response(data)




class CancelScheduledTaskApiView(APIView):

    def post(self, request, task_id):
        try:
            current_app.control.revoke(task_id, terminate=False)

            scheduled_task = TaskStatus.objects.get(task_id=task_id)
            scheduled_task.status = "CANCELLED"
            scheduled_task.save()

            return Response({"message": f"Task {task_id} cancelled successfully."})
        except TaskStatus.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)