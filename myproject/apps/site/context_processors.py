from django.conf import settings

def common(request):
    return {
        #'MEDIA_URL': settings.MEDIA_URL, # done request cp
        #'STATIC_URL': settings.STATIC_URL, # done using templatetag
    }
