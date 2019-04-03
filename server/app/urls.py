from django.urls import path
from .views import RegistrationAPI, LoginAPI, UserAPI

urlpatterns = [
    path("auth/register/", RegistrationAPI.as_view()),
    path("auth/login/", LoginAPI.as_view()),
    path("auth/user/", UserAPI.as_view()),
    # path("user/topic/", UserTopicAPI.as_view()),
    # path("group/topic/", GroupTopicAPI.as_view()),
]