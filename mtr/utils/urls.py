from django.conf.urls import patterns, url


urlpatterns = patterns(
    'mtr.utils.views',

    url(r'^model/(?P<name>.+)/pk/(?P<pk>\d+)$',
        'model_label', name='model_label')
)
