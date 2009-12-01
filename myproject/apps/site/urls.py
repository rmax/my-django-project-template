from django.conf.urls.defaults import *

urlpatterns = patterns('',
)

urlpatterns += patterns('django.views.generic.simple',
    url(r'^$', 'direct_to_template', {
            'template': 'site/home.html',
            'extra_context': {},
        }, name='site_home'),
)
