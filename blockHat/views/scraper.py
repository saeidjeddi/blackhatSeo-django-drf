from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from ..utils.tasks import request_data_task_simple
from ..models import TaskStatus
from accounts.jwtAuth import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import pytz
from ..utils.tasks import request_data_thread


class ScraperApiView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        url_request = request.query_params.get("url")
        range_request = request.query_params.get("range")
        user_agent_choice = request.query_params.get("user_agent", "all")
        referrers_choice = request.query_params.get("referrer", "https://www.facebook.com/")
        delay_seconds = request.query_params.get("delay")
        eta_time = request.query_params.get("eta")

        if not url_request or not range_request:
            return Response({"error": "url and range params are required!"}, status=400)

        try:
            range_request = int(range_request)
            if range_request < 1 or range_request > 1000:
                return Response({"error": "range must be between 1 and 1000!"}, status=400)
        except ValueError:
            return Response({"error": "range must be integer!"}, status=400)

        task_args = [url_request, range_request, user_agent_choice, referrers_choice]
        eta = None
        task = None

        london_tz = pytz.timezone("Europe/London")

        if delay_seconds:
            try:
                delay_seconds = int(delay_seconds)
                if delay_seconds < 0:
                    return Response({"error": "delay must be positive!"}, status=400)
            except ValueError:
                return Response({"error": "delay must be integer!"}, status=400)

            task = request_data_task_simple.apply_async(args=task_args, countdown=delay_seconds)
            eta = datetime.now(london_tz) + timedelta(seconds=delay_seconds)

        elif eta_time:
            try:
                eta = datetime.fromisoformat(eta_time)
            except ValueError:
                return Response({"error": "eta format invalid"}, status=400)

            if timezone.is_naive(eta):
                eta = london_tz.localize(eta)

            if eta <= datetime.now(london_tz):
                return Response({"error": "eta must be a future datetime!"}, status=400)

            task = request_data_task_simple.apply_async(args=task_args, eta=eta)

        else:
            task = request_data_task_simple.delay(*task_args)
            eta = datetime.now(london_tz)

        TaskStatus.objects.create(
            task_id=task.id,
            url=url_request,
            referer=referrers_choice,
            request_granted=range_request,
            completed_requests=0,
            status="PENDING",
            stop_requested=False
        )

        return Response({
            "message": f"Task scheduled for {range_request} requests to {url_request}",
            "task_id": task.id,
            "eta": eta.isoformat(),
            "user": request.user.username
        })
class ScraperThreadApiView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        url_request = request.query_params.get("url")
        range_request = request.query_params.get("range")
        user_agent_choice = request.query_params.get("user_agent", "all")
        referrers_choice = request.query_params.get("referrer", "https://www.facebook.com/")
        delay_seconds = request.query_params.get("delay")
        eta_time = request.query_params.get("eta")

        if not url_request or not range_request:
            return Response({"error": "url and range params are required!"}, status=400)

        try:
            range_request = int(range_request)
            if range_request < 1 or range_request > 1000:
                return Response({"error": "range must be between 1 and 1000!"}, status=400)
        except ValueError:
            return Response({"error": "range must be integer!"}, status=400)

        task_args = [url_request, range_request, user_agent_choice, referrers_choice]
        eta = None
        task = None
        london_tz = pytz.timezone("Europe/London")

        if delay_seconds:
            try:
                delay_seconds = int(delay_seconds)
                if delay_seconds < 0:
                    return Response({"error": "delay must be positive!"}, status=400)
            except ValueError:
                return Response({"error": "delay must be integer!"}, status=400)

            task = request_data_thread.apply_async(args=task_args, countdown=delay_seconds)
            eta = datetime.now(london_tz) + timedelta(seconds=delay_seconds)

        elif eta_time:
            try:
                eta = datetime.fromisoformat(eta_time)
            except ValueError:
                return Response({"error": "eta format invalid"}, status=400)

            if timezone.is_naive(eta):
                eta = london_tz.localize(eta)

            if eta <= datetime.now(london_tz):
                return Response({"error": "eta must be a future datetime!"}, status=400)

            task = request_data_thread.apply_async(args=task_args, eta=eta)

        else:
            task = request_data_thread.delay(*task_args)
            eta = datetime.now(london_tz)

        TaskStatus.objects.create(
            task_id=task.id,
            url=url_request,
            referer=referrers_choice,
            request_granted=range_request,
            completed_requests=0,
            status="PENDING",
            stop_requested=False
        )

        return Response({
            "message": f"Task scheduled for {range_request} requests to {url_request}",
            "task_id": task.id,
            "eta": eta.isoformat(),
            "user": request.user.username
        })
