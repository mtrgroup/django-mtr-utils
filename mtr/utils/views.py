from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

from mtr.utils.helpers import models_list, model_app_name


@staff_member_required
def model_label(request, name, pk):
    fmodel = None
    for model in models_list():
        if name == model_app_name(model):
            fmodel = model
            break

    result = ''

    if fmodel is not None:
        item = fmodel.objects.filter(pk=pk).first()

        if item is not None:
            result = getattr(
                item, 'admin_label', getattr(item, '__str__', ''))()

    return HttpResponse(result)
