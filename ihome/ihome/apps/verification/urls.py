from django.urls import re_path
from . import views

urlpatterns = [
    # 验证码
    re_path('imagecode$', views.Verification.as_view()),
    re_path('sms$', views.Sms.as_view()),
]
