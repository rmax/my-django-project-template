from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # local app urls here
    (r'', include('myproject.apps.site.urls')),
)
