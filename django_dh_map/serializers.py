from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from polymorphic.contrib.drf.serializers import PolymorphicSerializer

from .models import MapGeoJson, MapGeoJsonFeature, MapGeoJsonTransition, MapGeoJsonLabel, \
    Icon, IconImage, IconNumbered, \
    Map, OverheadImageMap, PanoramaImageMap, \
    XyzMap, \
    Feature, InfoPage, \
    ContentBlock, ContentBlockRichText, ContentBlockAudio, ContentBlockVideo, \
    ContentBlockImage, ContentBlockImageBeforeAndAfter, ContentBlockImageGallery, ContentBlockImageGalleryImage
# IconFont

# PolymorphicSerializers
# class IconFontSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IconFont
#         fields = ['id', 'class_value']

class IconImageSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(read_only=True)
    icon_thumbnail = serializers.ImageField(read_only=True)
    size = serializers.SerializerMethodField()
    class Meta:
        model = IconImage
        fields = ['id', 'thumbnail', 'icon_thumbnail', 'size']

    def get_size(self, obj):
        return obj.THUMBNAIL_SIZE

class IconNumberedSerializer(serializers.ModelSerializer):
    class Meta:
        model = IconNumbered
        fields = ['id', 'number']

class IconPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Icon: None,
        # IconFont: IconFontSerializer,
        IconImage: IconImageSerializer,
        IconNumbered: IconNumberedSerializer,
    }

    # needed for default/empty set
    class Meta:
        model = Icon
        fields = ['id']

class ContentBlockRichTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentBlockRichText
        fields = ['id', 'content']

class ContentBlockAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentBlockAudio
        fields = ['id', 'name', 'audio', 'license']

class ContentBlockVideoSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(read_only=True)
    class Meta:
        model = ContentBlockVideo
        fields = ['id', 'name', 'video', 'thumbnail', 'thumbnails_vtt', 'license']

class ContentBlockImageSerializer(serializers.ModelSerializer):
    web_resolution = serializers.ImageField(read_only=True)
    thumbnail = serializers.ImageField(read_only=True)
    class Meta:
        model = ContentBlockImage
        fields = ['id', 'name', 'original', 'web_resolution', 'thumbnail', 'description', 'license']

class ContentBlockImageBeforeAndAfterSerializer(serializers.ModelSerializer):
    before_web_resolution = serializers.ImageField(read_only=True)
    before_thumbnail = serializers.ImageField(read_only=True)
    after_web_resolution = serializers.ImageField(read_only=True)
    after_thumbnail = serializers.ImageField(read_only=True)
    class Meta:
        model = ContentBlockImageBeforeAndAfter
        fields = ['id', 'caption',
                  'before_original', 'before_web_resolution', 'before_thumbnail', 'before_description', 'before_license',
                  'after_original', 'after_web_resolution', 'after_thumbnail', 'after_description', 'after_license',
                 ]

class ContentBlockImageGalleryImageSerializer(serializers.ModelSerializer):
    web_resolution = serializers.ImageField(read_only=True)
    thumbnail = serializers.ImageField(read_only=True)
    class Meta:
        model = ContentBlockImageGalleryImage
        fields = ['id', 'name', 'original', 'web_resolution', 'thumbnail', 'description', 'license']

class ContentBlockImageGallerySerializer(serializers.ModelSerializer):
    images = ContentBlockImageGalleryImageSerializer(many=True)
    class Meta:
        model = ContentBlockImageGallery
        fields = ['id', 'images']


class ContentBlockPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        ContentBlock: None,
        ContentBlockRichText: ContentBlockRichTextSerializer,
        ContentBlockAudio: ContentBlockAudioSerializer,
        ContentBlockVideo: ContentBlockVideoSerializer,
        ContentBlockImage: ContentBlockImageSerializer,
        ContentBlockImageBeforeAndAfter: ContentBlockImageBeforeAndAfterSerializer,
        ContentBlockImageGallery: ContentBlockImageGallerySerializer,
    }
    # needed for default/empty set
    class Meta:
        model = ContentBlock
        fields = ['id']

# stubs
class FeatureStubSerializer(serializers.ModelSerializer):
    icon = IconPolymorphicSerializer()
    class Meta:
        model = Feature
        fields = ['id', 'title', 'published', 'icon']

# full records
class FeatureSerializer(serializers.ModelSerializer):
    icon = IconPolymorphicSerializer()
    content_blocks = ContentBlockPolymorphicSerializer(many=True)
    class Meta:
        model = Feature
        fields = ['id', 'title', 'published', 'icon', 'content_blocks']

class InfoPageSerializer(serializers.ModelSerializer):
    content_blocks = ContentBlockPolymorphicSerializer(many=True)
    class Meta:
        model = InfoPage
        fields = ['id', 'title', 'published', 'content_blocks']

class XyzMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = XyzMap
        fields = [
            'id', 'label', 'date_taken', 'license', 'published', 'data_srid', 'feature_srid', 'properties',
            'url', 'min_zoom', 'max_zoom', 'attributions',
        ]

class OverheadImageMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = OverheadImageMap
        fields = [
            'id', 'label', 'date_taken', 'license', 'published', 'data_srid', 'feature_srid', 'properties',
            'image', 'width', 'height', 'tiles_dir', 'tile_size', 'tile_format', 'min_zoom', 'max_zoom',
        ]

class PanoramaImageMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = PanoramaImageMap
        fields = [
            'id', 'label', 'date_taken', 'license', 'published', 'data_srid', 'feature_srid', 'properties',
            'image', 'width', 'height', 'tiles_dir', 'tile_size', 'tile_format', 'min_zoom', 'max_zoom',
            'cube_size',
        ]

class MapPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Map: None,
        XyzMap: XyzMapSerializer,
        OverheadImageMap: OverheadImageMapSerializer,
        PanoramaImageMap: PanoramaImageMapSerializer,
    }

    # needed for default/empty set
    class Meta:
        model = Map
        fields = ['id']

# GeoJson
class MapGeoJsonFeatureSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = MapGeoJsonFeature
        geo_field = 'geom_points'
        id_field = 'pk'
        fields = ['pk', 'feature', 'extra']

class MapGeoJsonTransitionSerializer(GeoFeatureModelSerializer):
    map = serializers.SerializerMethodField()

    class Meta:
        model = MapGeoJsonTransition
        geo_field = 'geom_points'
        id_field = 'pk'
        fields = ['pk', 'map', 'extra']

    def get_map(self, obj):
        return obj.destination_map_id

class MapGeoJsonLabelSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = MapGeoJsonLabel
        geo_field = 'geom_point'
        id_field = 'pk'
        fields = ['pk', 'label', 'extra']

class MapGeoJsonPolymorphicSerializer(PolymorphicSerializer, GeoFeatureModelSerializer):
    model_serializer_mapping = {
        MapGeoJson: None,
        MapGeoJsonFeature: MapGeoJsonFeatureSerializer,
        MapGeoJsonTransition: MapGeoJsonTransitionSerializer,
        MapGeoJsonLabel: MapGeoJsonLabelSerializer,
    }

    # needed for default/empty set
    class Meta:
        model = MapGeoJson
        geo_field = None
        id_field = 'pk'
        fields = ['pk', 'extra']

    def to_representation(self, instance):
        ret = super().to_representation(instance=instance)
        if self.resource_type_field_name:
            # move resourcetype to properties
            if isinstance(ret.get('properties'), dict):
                ret['properties'][self.resource_type_field_name] = ret[self.resource_type_field_name]
            # remove resourcetype from root feature geojson
            del ret[self.resource_type_field_name]
        return ret