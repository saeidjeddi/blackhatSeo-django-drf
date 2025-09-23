from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from ..models import TaskStatus
from ..serializers import ListHistoryTaskSerializer


class PageNumberPaginationResults(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class ListHistoryTaskStatusView(APIView):
    serializer_class = ListHistoryTaskSerializer
    pagination_class = PageNumberPaginationResults

    def get(self, request):
        tasks = TaskStatus.objects.all().order_by('-status', '-updated_at')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tasks, request)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(tasks, many=True)
        return Response(serializer.data)