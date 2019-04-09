from django.urls import path
from .views import *

urlpatterns = [
    path("auth/register/", RegistrationAPI.as_view()),
    path("auth/login/", LoginAPI.as_view()),
    path("auth/user/", UserAPI.as_view()),
    path('main/project/', ProjectAPI.as_view()),
    path('explore/news/', NewsAPI.as_view()),
    path('main/project_recommend/', Project_recommendAPI.as_view()),
    path('explore/popular/', Popular_projectAPI.as_view()),
    path('main/group/', GroupAPI.as_view()),
    path('notify/', NotifyAPI.as_view()),
    path('notify/read/', Notify_readAPI.as_view()),
    path('request/', RequestAPI.as_view()),
    path('request_accept/', Reqeust_acceptAPI.as_view()),
    path("search/", SearchAPI.as_view()),
    path("check/", CheckAPI.as_view()),
    path("follow/", User_followAPI.as_view()),
    path('group_entry/', Group_entryAPI.as_view()),
    path('idea/create/', Idea_createAPI.as_view()),
    path('idea/update/', Idea_updateAPI.as_view()),
    path('idea/delete/', Idea_deleteAPI.as_view()),
    path('idea/loc/create/', Idea_locCreateAPI.as_view()),
    path('idea/loc/update/', Idea_locUpdateAPI.as_view()),
    # path('main/', Project_createAPI.as_view()),
]