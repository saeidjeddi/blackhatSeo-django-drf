from django.urls import path

from .views.list_taskstatus_view import ListHistoryTaskStatusView
from .views.run_stop_task import StopTaskApiView, RunTaskApiView
from .views.uplode_proxy import ProxyUploadView
from .views.scraper import ScraperApiView, ScraperThreadApiView
from .views.taskstatus import TaskStatusInfoApiView
from .views.uplode_userAgent import UploadUserAgentsView
from .views.scheduledTaskList import ScheduledTaskListApiView, CancelScheduledTaskApiView

urlpatterns = [
    path('run-request/', ScraperApiView.as_view()),

    path('run-request-thread/', ScraperThreadApiView.as_view()),

    path("upload-proxies/", ProxyUploadView.as_view(), name="upload-proxies"),

    path('task-status-info/<str:task_id>/', TaskStatusInfoApiView.as_view()),

    path('list-history-task-status/', ListHistoryTaskStatusView.as_view()),

    path('upload-user-agents/', UploadUserAgentsView.as_view(), name='upload-user-agents'),

    path('stop-task/<str:task_id>/', StopTaskApiView.as_view()),

    path('run-stoped-task/<str:task_id>/', RunTaskApiView.as_view()),

    path('scheduled-task-list/', ScheduledTaskListApiView.as_view()),

    path('cancel-scheduled-task/<str:task_id>/', CancelScheduledTaskApiView.as_view()),
]