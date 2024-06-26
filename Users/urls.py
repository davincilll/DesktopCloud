# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('sendCode', views.sendCode, name='sendCode'),
    path('login', views.login, name='login'),
    path('register', views.register, name='regregister'),
    path('syncBookmarkConfig', views.syncBookmarkConfig, name='syncBookmarkConfig'),
    path('getBookmarkConfig', views.getBookmarkConfig, name='getBookmarkConfig')
]
