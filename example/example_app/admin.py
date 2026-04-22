from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from django.utils.encoding import force_str
from solo.admin import SingletonModelAdmin
from nested_admin.nested import NestedModelAdmin, NestedStackedInline
from nested_admin.polymorphic import NestedPolymorphicModelAdmin, NestedStackedPolymorphicInline

from django_dh_map.admin import DjangoDhMapAdminMixin, ContentBlockInline
from .models import HomePage, HomePageContent, WelcomeModal, WelcomeModalContent

class FixSingletonModelMixin():
    # Fix user message success vs info
    def response_change(self, request, obj):
        msg = _("{obj} was changed successfully.").format(obj=force_str(obj))
        if "_continue" in request.POST:
            self.message_user(request, msg + " " + _("You may edit it again below."), messages.SUCCESS)
            return HttpResponseRedirect(request.path)
        else:
            self.message_user(request, msg, messages.SUCCESS)
            return HttpResponseRedirect("../../")

class HomePageContentInline(NestedStackedInline):
    model = HomePageContent
    min_num = 0
    max_num = 1
    extra = 0
    inlines = [ContentBlockInline]

@admin.register(HomePage)
class HomePageAdmin(DjangoDhMapAdminMixin, FixSingletonModelMixin, SingletonModelAdmin, NestedPolymorphicModelAdmin):
    fields = [
        'title',
        'first_button_label', 'first_button_map',
        'second_button_label', 'second_button_map',
    ]
    inlines = [HomePageContentInline]

class WelcomeModalContentInline(NestedStackedInline):
    model = WelcomeModalContent
    min_num = 0
    max_num = 1
    extra = 0
    inlines = [ContentBlockInline]

@admin.register(WelcomeModal)
class WelcomeModalAdmin(DjangoDhMapAdminMixin, FixSingletonModelMixin, SingletonModelAdmin, NestedPolymorphicModelAdmin):
    fields = ['title', 'display', 'close_button_label']
    inlines = [WelcomeModalContentInline]