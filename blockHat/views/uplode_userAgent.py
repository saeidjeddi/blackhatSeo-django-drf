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

            if not file:
                return Response({"detail": "No file sent."}, status=status.HTTP_400_BAD_REQUEST)
            max_size = 1 * 1024 * 1024
            if file.size > max_size:
                return Response({"detail": "The file size is larger than 1 MB."}, status=status.HTTP_400_BAD_REQUEST)

            filename = file.name.lower()

            if not filename.endswith(".txt"):
                return Response({"detail": "Only .txt  files are allowed."}, status=status.HTTP_400_BAD_REQUEST)



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