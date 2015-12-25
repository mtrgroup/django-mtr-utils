from functools import partial

from .translation import _


class OriginalQuerysetMixin(object):

    def get_queryset(self, request):
        """Returns a QuerySet of all model instances without default
        manager 'objects' that can be edited by the
        admin site. This is used by changelist_view."""

        qs = self.model._base_manager.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class CopyActionMixin(object):

    def copy_object(self, request, queryset):
        # TODO: rewrite for all kind instances

        for item in queryset:
            fields = item.fields.all()
            contexts = item.contexts.all()

            item.id = None
            item.save()

            for field in fields:
                field.id = None
                field.settings_id = item.id
                field.save()

            for context in contexts:
                context.id = None
                context.settings_id = item.id
                context.save()

        self.message_user(
                request,
                _('Copies successfully created'))
    copy_object.short_description = _('Create a copy of settings')


class ObjectInlineMixin(object):

    def get_formset(self, request, obj=None, **kwargs):
        """Pass parent object to inline form"""

        kwargs['formfield_callback'] = partial(
            self.formfield_for_dbfield, request=request, obj=obj)
        return super(ObjectInlineMixin, self) \
            .get_formset(request, obj, **kwargs)
