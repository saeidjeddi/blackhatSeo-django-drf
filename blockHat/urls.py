from django.urls import path
from .views.uplode_proxy import ProxyUploadView
from .views.scraper import ScraperApiView
from .views.taskstatus import TaskStatusApiView
from .views.uplode_userAgent import UploadUserAgentsView
urlpatterns = [

    path('run-request/', ScraperApiView.as_view()),
    path("upload-proxies/", ProxyUploadView.as_view(), name="upload-proxies"),
    path('task-status/<str:task_id>/', TaskStatusApiView.as_view()),
    path('upload-user-agents/', UploadUserAgentsView.as_view(), name='upload-user-agents'),

]