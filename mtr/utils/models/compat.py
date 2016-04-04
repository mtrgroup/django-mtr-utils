from django.db import models
from django.utils import timezone

from ..translation import _


class PublishedManager(models.Manager):

    def get_queryset(self):
        return super(self, PublishedManager).get_queryset()\
            .filter(published=True, published_at__lt=timezone.now()) \
            .filter(
                models.Q(published_to__gt=timezone.now()) |
                models.Q(published_to=None))


class PublishedMixin(models.Model):
    published_at = models.DateTimeField(
        _('published at'), default=timezone.now)
    published_to = models.DateTimeField(
        _('published to'), null=True, blank=True)
    published = models.BooleanField(
        _('published (available)'), default=True)

    objects = models.Manager()
    published_objects = PublishedManager()

    class Meta:
        abstract = True
        index_together = ('published_at', 'published_to', 'published')
        ordering = ('-published_at', 'published')
