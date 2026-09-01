from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.conf import settings
from django.db.models import Q
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import JSONRenderer

class DefaultRouterWithUnregister(DefaultRouter):
    def unregister(self, prefix):
        # remove the prefix if exists
        self.registry = [item for item in self.registry if item[0] != prefix]
        # Clear the cached URLs so they re-generate on the next access
        if hasattr(self, '_urls'):
            delattr(self, '_urls')

from .serializers import MapGeoJsonPolymorphicSerializer, MapPolymorphicSerializer, \
    FeatureStubSerializer, FeatureSerializer, InfoPageSerializer
from .models import Map, MapGeoJson, Feature, InfoPage


class ReadOnlyModelListViewSet(ListModelMixin, GenericViewSet):
    pass

class ReadOnlyModelRetrieveViewSet(RetrieveModelMixin, GenericViewSet):
    pass

class GeoJsonRenderer(JSONRenderer):
    media_type = 'application/geo+json'

class BaseMapGeoJsonViewSet(ReadOnlyModelListViewSet):
    renderer_classes = [GeoJsonRenderer]
    queryset = MapGeoJson.objects
    serializer_class = MapGeoJsonPolymorphicSerializer
    # turn off pagination for GeoJson (send whole thing)
    pagination_class = None

    def get_queryset(self):
        return super().get_queryset().filter(map=self.kwargs['map_id'])

class AdminMapGeoJsonViewSet(BaseMapGeoJsonViewSet):
    permission_classes = [IsAdminUser]

class PublicMapGeoJsonViewSet(BaseMapGeoJsonViewSet):
    queryset = MapGeoJson.objects \
        .filter(Q(mapgeojsonfeature__feature__published=True) | Q(mapgeojsontransition__destination_map__published=True) | Q(mapgeojsonlabel__isnull=False)) \
        .filter(map__published=True)

    @method_decorator(cache_page(settings.CACHE_SECONDS))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class BaseFeatureViewSet(ReadOnlyModelViewSet):
    renderer_classes = [JSONRenderer]
    queryset = Feature.objects.prefetch_related('icon').all()
    serializer_class = FeatureSerializer

class AdminFeatureViewSet(BaseFeatureViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = FeatureStubSerializer

class PublicFeatureViewSet(BaseFeatureViewSet):
    queryset = Feature.objects.prefetch_related('content_blocks', 'icon').filter(published=True).all()

    @method_decorator(cache_page(settings.CACHE_SECONDS))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(settings.CACHE_SECONDS))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class BaseMapViewSet(ReadOnlyModelViewSet):
    renderer_classes = [JSONRenderer]
    queryset = Map.objects.all()
    serializer_class = MapPolymorphicSerializer

class AdminMapViewSet(BaseMapViewSet):
    permission_classes = [IsAdminUser]

class PublicMapViewSet(BaseMapViewSet):
    queryset = Map.objects.filter(published=True).all()

    @method_decorator(cache_page(settings.CACHE_SECONDS))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(settings.CACHE_SECONDS))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class InfoPageViewSet(ReadOnlyModelViewSet):
    renderer_classes = [JSONRenderer]
    queryset = InfoPage.objects.prefetch_related('content_blocks').filter(published=True).all()
    serializer_class = InfoPageSerializer

admin_router = DefaultRouterWithUnregister(use_regex_path=False, trailing_slash=False)
admin_router.register('maps/<int:map_id>/geojson', AdminMapGeoJsonViewSet)
admin_router.register('features', AdminFeatureViewSet)
admin_router.register('maps', AdminMapViewSet)

public_router = DefaultRouterWithUnregister(use_regex_path=False, trailing_slash=False)
public_router.register('maps/<int:map_id>/geojson', PublicMapGeoJsonViewSet)
public_router.register('features', PublicFeatureViewSet)
public_router.register('maps', PublicMapViewSet)
public_router.register('pages', InfoPageViewSet)