from django.db import models
from django.utils import timezone

from slugify import slugify
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

from .translation import _


class CharNullField(models.CharField):
    description = "CharField that stores NULL but returns empty string"
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, models.CharField):
            return value
        if value is None:
            return ''
        else:
            return value

    def get_prep_value(self, value):
        value = super(CharNullField, self).get_prep_value(value)

        if not value:
            return None
        else:
            return value


class SeoMixin(models.Model):
    seo_title = models.CharField(_('title'), max_length=100, blank=True)
    seo_description = models.CharField(
        _('description'), max_length=500, blank=True)
    seo_keywords = models.CharField(_('keywords'), max_length=300, blank=True)

    class Meta:
        abstract = True


class PublishedManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset() \
            .filter(
                published=True, published_at__lt=timezone.now()) \
            .filter(
                models.Q(published_to__gt=timezone.now()) |
                models.Q(published_to=None))


class TreePublishedManager(TreeManager, PublishedManager):
    pass


class PublishedMixin(models.Model):
    published_at = models.DateTimeField(
        _('published at'), default=timezone.now)
    published_to = models.DateTimeField(
        _('published to'), null=True, blank=True)
    published = models.BooleanField(_('published (available)'), default=True)

    objects = PublishedManager()

    class Meta:
        abstract = True
        index_together = ('published_at', 'published_to', 'published')
        ordering = ('-published_at', 'published')


class TreePublishedMixin(PublishedMixin):
    objects = TreePublishedManager()

    class Meta:
        abstract = True


class CreatedAtUpdatedAtMixin(models.Model):
    created_at_in_db = models.DateTimeField(
        _('created at'), auto_now_add=True, null=True)
    created_at = models.DateTimeField(
        _('created at'), default=timezone.now, editable=False)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class PositionRootMixin(models.Model):
    position = models.PositiveIntegerField(
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

    position = models.PositiveIntegerField(
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

    SLUG_PREFIXED_PARENT = 'parent'
    SLUG_PREFIXED_DUBLICATE = True

    parent = TreeForeignKey(
        'self', null=True, blank=True,
        related_name='children', verbose_name=_('parent'), db_index=True)

    class Meta:
        abstract = True

        verbose_name = _('category')
        verbose_name_plural = _('categories')

        ordering = ('position',)

        unique_together = ('slug', 'parent')

    class MPTTMeta:
        order_insertion_by = ('position',)

    def __str__(self):
        return self.name
