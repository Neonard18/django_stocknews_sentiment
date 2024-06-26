from django.urls import path, include
from rest_framework import routers
from .views import WatchListViewSet, AdminUserViewset, UserViewSet, PlottingViewSet
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

router = routers.DefaultRouter()
router.register('watch-list',WatchListViewSet)
router.register('admin',AdminUserViewset)
router.register('user',UserViewSet)
router.register('plot',PlottingViewSet)

urlpatterns = [
    path('',include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# when using the staticfiles_urlpatterns helper func, the url should include the file name
# domain.name/static/graph.png/
urlpatterns += staticfiles_urlpatterns()