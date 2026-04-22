from django.urls import include, path

# from . import views
from .api import admin_router, public_router

urlpatterns = [
    path('api/admin/', include(admin_router.urls)),
    path('api/', include(public_router.urls)),
]