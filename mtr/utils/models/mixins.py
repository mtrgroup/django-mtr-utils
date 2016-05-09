from django.db import models
from django.utils import timezone

from slugify import slugify
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

from .fields import CharNullField
from ..translation import _


class SeoMixin(models.Model):
    seo_title = models.CharField(_('title'), max_length=100, blank=True)
    seo_description = models.CharField(
        _('description'), max_length=500, blank=True)
    seo_keywords = models.CharField(_('keywords'), max_length=300, blank=True)

    class Meta:
        abstract = True


class PublishedQuerySet(models.QuerySet):

    def published(self):
        return self.filter(published=True, published_at__lt=timezone.now()) \
            .filter(
                models.Q(published_to__gt=timezone.now()) |
                models.Q(published_to=None))


class PublishedManager(models.Manager):

    def get_queryset(self):
        return PublishedQuerySet(self.model, using=self._db).published()


class TreePublishedManager(TreeManager, PublishedManager):

    def get_queryset(self):
        return PublishedQuerySet(self.model, using=self._db).published()


class PublishedMixin(models.Model):
    published_at = models.DateTimeField(
        _('published at'), default=timezone.now)
    published_to = models.DateTimeField(
        _('published to'), null=True, blank=True)
    published = models.BooleanField(
        _('published (available)'), default=True)

    objects = models.Manager.from_queryset(PublishedQuerySet)()
    published_objects = PublishedManager()

    class Meta:
        abstract = True
        index_together = ('published_at', 'published_to', 'published')
        ordering = ('-published_at', 'published')

    def is_published(self):
        now = timezone.now()
        published = self.published and self.published_at < now
        if self.published_to:
            published = published and self.published_to < now
        return published


class TreePublishedMixin(PublishedMixin):
    objects = TreeManager()
    published_objects = TreePublishedManager()

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    # TODO: add custom naming mixin

    created_at_in_db = models.DateTimeField(
        _('created at'), auto_now_add=True, null=True)
    created_at = models.DateTimeField(
        _('created at'), default=timezone.now, editable=False)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class PositionRootMixin(models.Model):
    position = models.BigIntegerField(
        _('position'), null=True, blank=True, default=-1)

    class Meta:
        abstract = True

        ordering = ('position',)

    def save(self, *args, **kwargs):
        if self.position == -1:
            self.position = self.__class__.objects \
                .aggregate(models.Max('position'))['position__max']
            self.position = self.position + 1 if self.position else 0

        super(PositionRootMixin, self).save(*args, **kwargs)


class PositionRelatedMixin(models.Model):
    POSITION_RELATED_FIELD = None

    position = models.BigIntegerField(
        _('position'), null=True, blank=True, default=-1)

    class Meta:
        abstract = True

        ordering = ('position',)

    def save(self, *args, **kwargs):
        related_field = getattr(self, self.POSITION_RELATED_FIELD, None)

        if self.position == -1:
            self.position = self.__class__.objects
            if related_field is not None:
                self.position = self.position.filter(**{
                    self.POSITION_RELATED_FIELD: related_field})
            self.position = self.position.aggregate(
                models.Max('position'))['position__max']
            self.position = self.position + 1 if self.position else 0

        super(PositionRelatedMixin, self).save(*args, **kwargs)


class SlugifyNameMixin(models.Model):
    SLUG_PREFIXED_DUBLICATE = False
    SLUG_PREFIXED_PARENT = None

    slug = CharNullField(
        _('slug'), max_length=300, db_index=True, blank=True, null=True)
    base_slug = models.CharField(
        _('base slug'), max_length=300, blank=True)
    name = models.CharField(_('name'), max_length=300, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        overwrite_slug = kwargs.pop('overwrite_slug', False)
        prefixed_dublicate = kwargs.pop(
            'prefixed_dublicate', self.SLUG_PREFIXED_DUBLICATE)

        if not self.slug and self.name or overwrite_slug:
            self.slug = slugify(self.name)

            if self.SLUG_PREFIXED_PARENT is not None:
                parent = getattr(getattr(
                    self, self.SLUG_PREFIXED_PARENT, None), 'slug', None)
                if parent:
                    self.slug = '/'.join([parent, self.slug])

            if not self.base_slug or overwrite_slug:
                self.base_slug = self.slug

            if prefixed_dublicate:
                count = self.__class__.objects \
                    .filter(base_slug=self.base_slug).count()
                if count:
                    self.slug = '{}-{}'.format(self.base_slug, count)

        super().save(*args, **kwargs)


class TreeParentMixin(
        MPTTModel, SlugifyNameMixin,
        TreePublishedMixin, PositionRelatedMixin):
    POSITION_RELATED_FIELD = 'parent'

    RELATED_COUNT_TO = None
    RELATED_COUNT_MANAGER = 'published_objects'

    SLUG_PREFIXED_PARENT = 'parent'
    SLUG_PREFIXED_DUBLICATE = True

    parent = TreeForeignKey(
        'self', null=True, blank=True,
        related_name='children', verbose_name=_('parent'), db_index=True)

    class Meta:
        abstract = True

        ordering = ('position',)

        unique_together = ('slug', 'parent')

    class MPTTMeta:
        order_insertion_by = ('position',)

    class Settings:
        position = {'related': 'parent'}
        count = {'related': None, 'manager': 'published_objects'}
        slug = {'related': 'parent', 'dublicate': True}

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        recalc = kwargs.pop('recalc', True)

        super().save(*args, **kwargs)

        if recalc and self.RELATED_COUNT_TO:
            self.calculate_related_count()

    def calculate_related_count(self):
        curr_level = None

        for category in reversed(self.get_family()):
            if curr_level is None:
                curr_level = category.level

            if curr_level > category.level:
                count = category.children \
                    .aggregate(models.Sum('count'))['count__sum']
            else:
                count = getattr(category, self.RELATED_COUNT_TO)
                count = getattr(count.model, self.RELATED_COUNT_MANAGER) \
                    .filter(category=category).count()
            self.__class__.objects.filter(id=category.id).update(count=count)


class ValidateOnSaveMixin(object):
    # https://www.xormedia.com/django-model-validation-on-save/

    def save(self, force_insert=False, force_update=False, **kwargs):
        if not (force_insert or force_update):
            self.full_clean()
        super(ValidateOnSaveMixin, self).save(
            force_insert, force_update, **kwargs)


class StyleMixin(models.Model):
    # TODO: ->
    # render_string (idea from logger)
    # and one to many settings with colors and render params

    class Meta:
        abstract = True
