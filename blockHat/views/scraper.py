from rest_framework.views import APIView
from rest_framework.response import Response
from ..utils.tasks import request_data_task

class ScraperApiView(APIView):

    def get(self, request):
        url_request = request.query_params.get("url")
        range_request = request.query_params.get("range")
        user_agent_choice = request.query_params.get("user_agent", "all")
        referrers_choice = request.query_params.get("referrer", "https://www.facebook.com/")

        if not url_request or not range_request:
            return Response({"error": "url and range params are required!"}, status=400)

        try:
            range_request = int(range_request)
            if range_request < 1 or range_request > 1000:
                return Response({"error": "range must be between 1 and 1000!"}, status=400)
        except ValueError:
            return Response({"error": "range must be integer!"}, status=400)

        task = request_data_task.delay(url_request, range_request, user_agent_choice, referrers_choice)

        return Response({
            "message": f"Task started for {range_request} requests to {url_request}",
            "task_id": task.id
        })
