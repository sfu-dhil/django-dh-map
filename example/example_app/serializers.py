from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from polymorphic.contrib.drf.serializers import PolymorphicSerializer

from django_dh_map.serializers import ContentBlockPolymorphicSerializer

from .models import WelcomeModal, WelcomeModalContent


class WelcomeModalContentSerializer(serializers.ModelSerializer):
    content_blocks = ContentBlockPolymorphicSerializer(many=True)
    class Meta:
        model = WelcomeModalContent
        fields = ['content_blocks']

class WelcomeModalSerializer(serializers.ModelSerializer):
    content_item = WelcomeModalContentSerializer()
    class Meta:
        model = WelcomeModal
        fields = ['title', 'display', 'close_button_label', 'content_item']
