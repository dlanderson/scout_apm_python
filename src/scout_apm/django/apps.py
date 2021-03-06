from __future__ import absolute_import

from django.apps import AppConfig

from scout_apm.django.instruments.sql import SQLInstrument
from scout_apm.django.instruments.template import TemplateInstrument
from scout_apm.django.config import ConfigAdapter
import scout_apm.core

import logging


logger = logging.getLogger(__name__)


class ScoutApmDjangoConfig(AppConfig):
    name = 'scout_apm'
    verbose_name = 'Scout Apm (Django)'

    def ready(self):
        # Copy django configuration to scout_apm's config
        ConfigAdapter.install()

        # Finish installing the agent. If the agent isn't installed for any
        # reason, return without installing instruments
        installed = scout_apm.core.install()
        if installed is False:
            return

        self.install_middleware()

        # Setup Instruments
        SQLInstrument.install()
        TemplateInstrument.install()

    def install_middleware(self):
        """
        Attempts to insert the ScoutApm middleware as the first middleware
        (first on incoming requests, last on outgoing responses).
        """
        from django.conf import settings

        # If MIDDLEWARE_CLASSES is set, update that, with handling of tuple vs array forms
        if settings.MIDDLEWARE_CLASSES is not None:
            if isinstance(settings.MIDDLEWARE_CLASSES, tuple):
                settings.MIDDLEWARE_CLASSES = (
                    ('scout_apm.django.middleware.OldStyleMiddlewareTimingMiddleware', ) +
                    settings.MIDDLEWARE_CLASSES +
                    ('scout_apm.django.middleware.OldStyleViewMiddleware', ))
            else:
                settings.MIDDLEWARE_CLASSES.insert(0, 'scout_apm.django.middleware.OldStyleMiddlewareTimingMiddleware')
                settings.MIDDLEWARE_CLASSES.append('scout_apm.django.middleware.OldStyleViewMiddleware')

        # Otherwise, we're doing new style middleware, do the same thing with
        # the same handling of tuple vs array forms
        else:
            if isinstance(settings.MIDDLEWARE, tuple):
                settings.MIDDLEWARE = (
                    ('scout_apm.django.middleware.MiddlewareTimingMiddleware', ) +
                    settings.MIDDLEWARE +
                    ('scout_apm.django.middleware.ViewTimingMiddleware', ))
            else:
                settings.MIDDLEWARE.insert(0, 'scout_apm.django.middleware.MiddlewareTimingMiddleware')
                settings.MIDDLEWARE.append('scout_apm.django.middleware.ViewTimingMiddleware')

