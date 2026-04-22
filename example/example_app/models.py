from django.db import models
from django.utils.safestring import mark_safe
from django.db.models import Q
from solo.models import SingletonModel

from django_dh_map.models import ContentItem, Map, XyzMap, OverheadImageMap, PanoramaImageMap

class HomePage(SingletonModel):
    title = models.CharField(default='Example App')

    first_button_label = models.CharField(verbose_name='First Button Label', default='View Map')
    first_button_map = models.ForeignKey(
        Map,
        null=True,
        related_name='home_page_first_button',
        on_delete=models.CASCADE,
        verbose_name='First Button Map',
        limit_choices_to=Q(published=True),
    )
    second_button_label = models.CharField(verbose_name='Second Button Label', default='View Panorama')
    second_button_map = models.ForeignKey(
        PanoramaImageMap,
        null=True,
        related_name='home_page_second_button',
        on_delete=models.CASCADE,
        verbose_name='Second Button Map',
        limit_choices_to=Q(published=True),
    )

    # relationships
    # one-to-one content_item via HomePageContent Model

    class Meta:
        db_table = 'example_app_home_page'
        verbose_name = 'Home Page'

    def __str__(self):
        return f'{self.title}'

class HomePageContent(ContentItem):
    # relationships
    home_page = models.OneToOneField(
        HomePage,
        related_name='content_item',
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'example_app_ci_home_page'
        verbose_name = 'Home Page Content'

class WelcomeModal(SingletonModel):
    title = models.CharField(default='Welcome')
    display = models.BooleanField(verbose_name='Display?', default=False, db_index=True)
    close_button_label = models.CharField(default='Close')

    # relationships
    # one-to-one content_item via WelcomeModalContent Model

    class Meta:
        db_table = 'example_app_welcome_modal'
        verbose_name = 'Welcome Modal'

    def __str__(self):
        return f'{self.title}'

class WelcomeModalContent(ContentItem):
    # relationships
    welcome_modal = models.OneToOneField(
        WelcomeModal,
        related_name='content_item',
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'example_app_ci_welcome_modal'
        verbose_name = 'Welcome Modal Content'