from django.urls import path
from django.views.decorators.cache import cache_page
from django.conf import settings

from . import views
from . import api

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('app', views.AppView.as_view(), name='app'),
    path('api/content', api.static_content),
]