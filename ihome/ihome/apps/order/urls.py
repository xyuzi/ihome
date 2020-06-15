from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'orders/(?P<pk>\d+)/status$', views.OrdersStatusView.as_view()),
    re_path(r'orders/(?P<pk>\d+)/comment$', views.OrdersCommentView.as_view()),
    re_path(r'orders$', views.OrdersView.as_view()),
]
