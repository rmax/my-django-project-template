from django import template
from django.conf import settings

import logging
import os

try:
    from hashlib import md5
except ImportError:
    #python 2.4
    from md5 import md5

register = template.Library()

def static_url(path):
    """Returns url using STATIC_URL with hash ?v=####
       based on modified file time
    """
    if not hasattr(settings, '_STATIC_HASHES'):
        settings._STATIC_HASHES = {}
    hashes = settings._STATIC_HASHES
    if path not in hashes:
        try:
            #@@@ use: with open(...) as f:  (python >2.5)
            f = open(os.path.join(settings.STATIC_ROOT, path), 'rb')
            #TODO: use pluggable file storage to read file
            #@@@ not use on too big files
            hashes[path] = md5(f.read()).hexdigest()
            f.close()
        except Exception, e:
            logging.error("Could not open static file %r: %s", path, e)
            hashes[path] = None

    url = settings.STATIC_URL + path
    if hashes.get(path):
        return '%s?v=%s' % (url, hashes[path][:5])
    else:
        return url

def media_url(path):
    """Returns url using MEDIA_URL
       logs error if file not exists
    """
    #TODO: use pluggable file storage to read file

    if not hasattr(settings, '_MEDIA_EXISTS'):
        settings._MEDIA_EXISTS = {}
    exists = settings._MEDIA_EXISTS

    file = settings.MEDIA_ROOT + path
    if path not in exists:
        if not os.path.exists(file):
            logging.error("Could not open media file %r: %s", path)
            exists[path] = False
        else:
            exists[path] = True

    url = settings.MEDIA_URL + path
    return url


###
register.simple_tag(static_url)
register.simple_tag(media_url)
