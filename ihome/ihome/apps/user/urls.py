from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'users$', views.Users.as_view()),
    re_path(r'session$', views.UsersLogin.as_view()),
    re_path(r'user$', views.UserInfo.as_view()),
    re_path(r'user/avatar$', views.UserInfoAvatar.as_view()),
    re_path(r'user/name$', views.UserInfoName.as_view()),
    re_path(r'user/auth$', views.UserInfoAuth.as_view()),
    re_path(r'user/houses$', views.UserInfoHouses.as_view()),
]
