from django import forms
from django.db import models
from django.utils.safestring import mark_safe

from .models import OverheadImageMap, PanoramaImageMap, XyzMap

class GeoJsonWidget(forms.Textarea):
    instance = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['hidden'] = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.instance:
            if isinstance(self.instance, XyzMap) and self.instance.url:
                context['widget']['instance'] = self.instance
                self.template_name = 'django_dh_map/forms/widgets/openlayers_features_change_app.html'
            elif isinstance(self.instance, OverheadImageMap) and self.instance.has_tiles():
                context['widget']['instance'] = self.instance
                self.template_name = 'django_dh_map/forms/widgets/openlayers_features_change_app.html'
            elif isinstance(self.instance, PanoramaImageMap) and self.instance.has_tiles():
                context['widget']['instance'] = self.instance
                self.template_name = 'django_dh_map/forms/widgets/pannellum_features_change_app.html'
        return context

class TextDataListWidget(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name
        self._data_list = data_list
        self.attrs.update({'list': f'list__{self._name}'})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super().render(name, value, attrs=attrs, renderer=renderer)
        data_list_html = f'<datalist id="list__{self._name}">'
        if isinstance(self._data_list, models.Choices):
            for choice in self._data_list:
                data_list_html += f'<option value="{choice.value}">{choice.label}</option>'
        elif isinstance(self._data_list, dict):
            for value, label in self._data_list.items():
                data_list_html += f'<option value="{value}">{label}</option>'
        elif isinstance(self._data_list, list):
            for value in self._data_list:
                data_list_html += f'<option value="{value}" />'
        data_list_html += '</datalist>'

        return mark_safe(text_html + data_list_html)