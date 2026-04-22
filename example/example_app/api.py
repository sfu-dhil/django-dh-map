from django.views.decorators.cache import cache_page
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .serializers import WelcomeModalSerializer
from .models import WelcomeModal

@cache_page(settings.CACHE_SECONDS)
@api_view(["GET"])
def static_content(request):
    return Response({
        'welcome': WelcomeModalSerializer(WelcomeModal.get_solo()).data,
    })
