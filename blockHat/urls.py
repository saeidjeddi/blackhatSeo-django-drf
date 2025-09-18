from django.urls import path
from .views import ListTextApi

urlpatterns = [

    path('', ListTextApi.as_view())
]