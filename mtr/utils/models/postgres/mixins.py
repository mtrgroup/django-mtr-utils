from django.db import models
from django.contrib.postgres.fields import ArrayField


from ..translation import _


class ViewsCountMixin(models.Model):
    views_count = models.BigIntegerField(
        _('views'), default=0, db_index=True)
    views_ips = ArrayField(
        models.CharField(
            _('ips'), max_length=45), null=True, db_index=True)

    class Meta:
        abstract = True

    def process_view(self, ip):
        ips = self.views_ips or []
        if ip not in ips:
            ips.append(ip)

            self.views_ips = ips
            self.views_count = models.F('views_count') + 1
            self.save(update_fields=['views_ips', 'views_count'])


class ImagesMixin(models.Model):
    image_list = ArrayField(
        models.ImageField(_('image')), blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.image_list = []
        for image in self.images.all():
            try:
                self.image_list.append(str(image.file))
            except ValueError:
                pass

        super().save(*args, **kwargs)

    @property
    def main_image(self):
        return self.image_list[0] if self.image_list else None

    # def preview(self):
    #     try:
    #         thumbnail = get_thumbnail(self.main_image, '50x50')

    #         return '<img src="{}" width="{}" height="{}">'.format(
    #             thumbnail.url, thumbnail.width, thumbnail.height)
    #     except:
    #         return None
    # preview.allow_tags = True
    # preview.short_description = _('Preview')
    # preview.admin_order_field = 'image_list'
