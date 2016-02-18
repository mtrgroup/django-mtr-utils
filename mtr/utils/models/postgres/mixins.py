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

            # TODO: use F()
            self.views_ips = ips
            self.views_count += 1
            self.save(update_fields=['views_ips', 'views_count'])
