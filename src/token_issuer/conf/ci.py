"""
Continuous integration settings module.
"""
import logging
import os

os.environ.setdefault("IS_HTTPS", "no")
os.environ.setdefault("SECRET_KEY", "dummy")

from .base import *  # noqa isort:skip

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    # See: https://github.com/jazzband/django-axes/blob/master/docs/configuration.rst#cache-problems
    "axes": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
}

LOGGING = None  # Quiet is nice
logging.disable(logging.CRITICAL)

ENVIRONMENT = "CI"

#
# Django-axes
#
AXES_BEHIND_REVERSE_PROXY = False
