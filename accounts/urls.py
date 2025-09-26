from django.urls import path
from .views import AccountsAllUserAPIView


urlpatterns = [
    path('users/', AccountsAllUserAPIView.as_view()),
]