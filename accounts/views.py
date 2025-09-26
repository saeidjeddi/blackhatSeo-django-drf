from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer


class AccountsAllUserAPIView(APIView):
    serializer_class = UserSerializer

    def get(self, request):
        users = User.objects.using('user_cid').all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)