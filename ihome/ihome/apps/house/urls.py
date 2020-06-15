from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'areas$', views.AreasView.as_view()),
    re_path(r'houses/index$', views.HousesIndexView.as_view()),
    re_path(r'houses/(?P<house_id>\d+)/images$', views.HousesImageView.as_view()),
    re_path(r'houses/(?P<pk>\d+)$', views.HousesInfoView.as_view()),
    re_path(r'houses$', views.HousesView.as_view()),
]
