from rest_framework.views import APIView
from rest_framework.response import Response
from blockHat.models import TaskStatus
from ..utils.tasks import request_data_task_simple

class StopTaskApiView(APIView):

    def post(self, request, task_id):
        try:
            task_status = TaskStatus.objects.get(task_id=task_id)
            task_status.stop_requested = True
            task_status.status = "STOPPED"
            task_status.save()
            
            scheduled_task = TaskStatus.objects.filter(task_id=task_id).first()
            if scheduled_task:
                scheduled_task.status = "STOPPED"
                scheduled_task.save()
            
            return Response({"message": f"Task {task_id} stopped successfully."})
        except TaskStatus.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)


            
class RunTaskApiView(APIView):
    def post(self, request, task_id):
        try:
            task_status = TaskStatus.objects.get(task_id=task_id)
            if task_status.status != "STOPPED":
                return Response({"error": "Task is not stopped!"}, status=400)

            task_status.stop_requested = False
            task_status.status = "RUNNING"
            task_status.save()

            url_request = task_status.url
            range_request = task_status.request_granted
            user_agent_choice = "all"
            referrers_choice = task_status.referer

            request_data_task_simple.apply_async(
                args=[url_request, range_request, user_agent_choice, referrers_choice],
                task_id=task_id
            )

            return Response({"message": f"Task {task_id} resumed successfully."})
        except TaskStatus.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)
