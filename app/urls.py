from django.urls import path, include
from rest_framework import routers
from .views import WatchListViewSet, UserViewSet, PlottingViewSet
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

router = routers.DefaultRouter()
router.register('watch-list',WatchListViewSet)
router.register('user',UserViewSet)
router.register('plot',PlottingViewSet)

urlpatterns = [
    path('',include(router.urls)),
]

urlpatterns += staticfiles_urlpatterns(settings.STATIC_URL, document_root=settings.STATIC_ROOT)