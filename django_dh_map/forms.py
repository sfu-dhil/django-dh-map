from django import forms
from django.contrib.gis.geos import MultiPoint, Point

from .models import Map, OverheadImageMap, PanoramaImageMap, \
    XyzMap, \
    MapGeoJsonFeature, MapGeoJsonTransition, MapGeoJsonLabel
from .widgets import GeoJsonWidget

class BaseMapAdminForm(forms.ModelForm):
    map_geojson = forms.JSONField(label='Map Features', required=False, widget=GeoJsonWidget())

    class Meta:
        model = Map
        fields = ['label', 'date_taken', 'published', 'license', 'properties']
        widgets = { 'properties': forms.HiddenInput }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['map_geojson'].widget.instance = self.instance
        self.fields['map_geojson'].initial = None

    def save(self, commit=True):
        map = super().save(commit=False)
        form_map_geojson = self.cleaned_data.get('map_geojson')
        if form_map_geojson and form_map_geojson.get('type') == 'FeatureCollection' and isinstance(form_map_geojson.get('features'), list):
            existing_map_geojson_dict = {
                map_geojson.pk: map_geojson for map_geojson in map.map_geojson.all()
            }
            update_set = []
            for feature_geojson in form_map_geojson.get('features'):
                existing_id = feature_geojson.get('id')
                map_geojson = existing_map_geojson_dict.get(existing_id, None)
                coords = feature_geojson.get('geometry', {}).get('coordinates', [])
                properties = feature_geojson.get('properties', {})

                # skip/remove if empty
                if len(coords) == 0:
                    continue

                if map_geojson:
                    del existing_map_geojson_dict[existing_id]
                elif properties.get('resourcetype') == MapGeoJsonFeature.__name__:
                    map_geojson = MapGeoJsonFeature(map=map, feature_id=properties.get('feature'))
                elif properties.get('resourcetype') == MapGeoJsonTransition.__name__:
                    map_geojson = MapGeoJsonTransition(map=map, destination_map_id=properties.get('map'))
                elif properties.get('resourcetype') == MapGeoJsonLabel.__name__:
                    map_geojson = MapGeoJsonLabel(map=map)

                # add if valid
                if map_geojson is not None:
                    if properties.get('resourcetype') == MapGeoJsonFeature.__name__:
                        map_geojson.geom_points = MultiPoint([Point(c) for c in coords],srid=map.data_srid)
                    elif properties.get('resourcetype') == MapGeoJsonTransition.__name__:
                        map_geojson.geom_points = MultiPoint([Point(c) for c in coords],srid=map.data_srid)
                    elif properties.get('resourcetype') == MapGeoJsonLabel.__name__:
                        map_geojson.geom_point = Point(coords,srid=map.data_srid)
                        map_geojson.label = properties.get('label')

                    map_geojson.extra = properties.get('extra', {})
                    map_geojson.save()
                    update_set.append(map_geojson)
            map.map_geojson.set(update_set)
            # remove old geojson
            for map_geojson in existing_map_geojson_dict.values():
                map_geojson.delete()
        if commit:
            map.save(commit=True)
        return map

class XyzMapForm(BaseMapAdminForm):
    class Meta:
        model = XyzMap
        fields = [
            'label', 'date_taken', 'published',
            'feature_srid', 'url', 'min_zoom', 'max_zoom', 'attributions',
            'license', 'properties'
        ]
        widgets = { 'properties': forms.HiddenInput }

class OverheadImageMapForm(BaseMapAdminForm):
    class Meta:
        model = OverheadImageMap
        fields = [
            'label', 'date_taken', 'published',
            'image',
            'license', 'properties'
        ]
        widgets = { 'properties': forms.HiddenInput }

class PanoramaImageMapForm(BaseMapAdminForm):
    class Meta:
        model = PanoramaImageMap
        fields = [
            'label', 'date_taken', 'published',
            'image',
            'license', 'properties'
        ]
        widgets = { 'properties': forms.HiddenInput }