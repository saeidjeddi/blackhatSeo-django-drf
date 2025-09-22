from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user_agents import parse
from ..serializers import UserAgentFileUploadSerializer
from ..models import UserAgentDesktop, UserAgentMobile


class UploadUserAgentsView(APIView):
    def post(self, request):
        serializer = UserAgentFileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']

            for line in file:
                ua_string = line.decode('utf-8').strip()
                if not ua_string:
                    continue

                user_agent = parse(ua_string)

                if user_agent.is_mobile or user_agent.is_tablet:
                    UserAgentMobile.objects.create(user_agent=ua_string)
                else:
                    UserAgentDesktop.objects.create(user_agent=ua_string)

            return Response({"message": "User-Agents saved!"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)