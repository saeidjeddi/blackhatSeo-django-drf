from django.urls import path
from .views.uplode_proxy import ProxyUploadView
from .views.scraper import ScraperApiView

urlpatterns = [

    path('run-request/', ScraperApiView.as_view()),
    path("upload-proxies/", ProxyUploadView.as_view(), name="upload-proxies"),

]