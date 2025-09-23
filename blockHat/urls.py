from django.urls import path

from .views.list_taskstatus_view import ListHistoryTaskStatusView
from .views.uplode_proxy import ProxyUploadView
from .views.scraper import ScraperApiView
from .views.taskstatus import TaskStatusInfoApiView
from .views.uplode_userAgent import UploadUserAgentsView
urlpatterns = [
    path('run-request/', ScraperApiView.as_view()),
    path("upload-proxies/", ProxyUploadView.as_view(), name="upload-proxies"),
    path('task-status-info/<str:task_id>/', TaskStatusInfoApiView.as_view()),
    path('list-history-task-status/', ListHistoryTaskStatusView.as_view()),
    path('upload-user-agents/', UploadUserAgentsView.as_view(), name='upload-user-agents'),
]