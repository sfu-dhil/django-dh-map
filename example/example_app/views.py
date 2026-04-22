import json
from django.views.generic import TemplateView

from django_dh_map.serializers import ContentBlockPolymorphicSerializer

from .models import HomePage

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        home_page = HomePage.get_solo()
        if home_page and hasattr(home_page, 'content_item'):
            content_blocks = home_page.content_item.content_blocks
            context['content_blocks_json'] = json.dumps(ContentBlockPolymorphicSerializer(content_blocks, many=True).data)
        else:
            context['content_blocks_json'] = json.dumps([])
        return context

class AppView(TemplateView):
    template_name = 'app.html'
