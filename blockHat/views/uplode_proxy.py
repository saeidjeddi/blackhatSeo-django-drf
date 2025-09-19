
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from blockHat.models import Proxy
from blockHat.serializers import ProxySerializer


class ProxyUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ProxySerializer

    def post(self, request, format=None):
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file sent."}, status=status.HTTP_400_BAD_REQUEST)
        max_size = 1 * 1024 * 1024 # 1MB
        if file.size > max_size:
            return Response({"detail": "The file size is larger than 1 MB."}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.lower().endswith(".txt"):
            return Response({"detail": "Only .txt files are allowed."}, status=status.HTTP_400_BAD_REQUEST)


        content = file.read().decode("utf-8").splitlines()

        added, skipped = 0, 0
        for line in content:
            line = line.strip()
            if not line:
                continue
            obj, created = Proxy.objects.get_or_create(proxy_test=line)
            if created:
                added += 1
            else:
                skipped += 1

        return Response({
            "total": len(content),
            "added": added,
            "skipped": skipped
        }, status=status.HTTP_201_CREATED)
