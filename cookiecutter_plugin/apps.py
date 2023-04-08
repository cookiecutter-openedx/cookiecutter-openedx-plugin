# coding=utf-8
"""
written by:     Lawrence McDaniel
                https://lawrencemcdaniel.com

date:           apr-2023

usage:          Django app and Open edX plugin configuration
"""
import json
import logging

from django.apps import AppConfig

# see: https://github.com/openedx/edx-django-utils/blob/master/edx_django_utils/plugins/
from edx_django_utils.plugins import PluginSettings, PluginURLs
from openedx.core.djangoapps.plugins.constants import (
    ProjectType,
    SettingsType,
    PluginSignals,
)


# Signals (aka receivers) defined in https://github.com/openedx/openedx-events/blob/main/openedx_events/learning/signals.py
CERTIFICATE_CREATED = "CERTIFICATE_CREATED"
CERTIFICATE_CHANGED = "CERTIFICATE_CHANGED"
CERTIFICATE_REVOKED = "CERTIFICATE_REVOKED"

OPENEDX_SIGNALS_PATH = "openedx_events.learning.signals"
OPENEDX_SIGNALS = [
    CERTIFICATE_CREATED,
    CERTIFICATE_CHANGED,
    CERTIFICATE_REVOKED,
]

log = logging.getLogger(__name__)
IS_READY = False


class CookiecutterPluginConfig(AppConfig):
    name = "cookiecutter_plugin"
    label = "cookiecutter_plugin"

    # This is the text that appears in the Django admin console in all caps
    # as the title box encapsulating all Django app models that are registered
    # in admin.py.
    verbose_name = "Cookiecutter Open edX plugin"

    # See: https://edx.readthedocs.io/projects/edx-django-utils/en/latest/edx_django_utils.plugins.html
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: name,
                PluginURLs.REGEX: "^cookiecutter_plugin/",
                PluginURLs.RELATIVE_PATH: "urls",
            }
        },
        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                SettingsType.COMMON: {PluginSettings.RELATIVE_PATH: "settings.common"},
            }
        },
        PluginSignals.CONFIG: {
            ProjectType.LMS: {
                PluginSignals.RELATIVE_PATH: "signals",
                PluginSignals.RECEIVERS: [
                    {
                        PluginSignals.RECEIVER_FUNC_NAME: CERTIFICATE_CREATED.lower(),
                        PluginSignals.SIGNAL_PATH: OPENEDX_SIGNALS_PATH + "." + CERTIFICATE_CREATED,
                    },
                    {
                        PluginSignals.RECEIVER_FUNC_NAME: CERTIFICATE_CHANGED.lower(),
                        PluginSignals.SIGNAL_PATH: OPENEDX_SIGNALS_PATH + "." + CERTIFICATE_CHANGED,
                    },
                    {
                        PluginSignals.RECEIVER_FUNC_NAME: CERTIFICATE_REVOKED.lower(),
                        PluginSignals.SIGNAL_PATH: OPENEDX_SIGNALS_PATH + "." + CERTIFICATE_REVOKED,
                    },
                ],
            }
        },
    }

    def ready(self):
        global IS_READY

        if IS_READY:
            return

        from . import signals  # pylint: disable=unused-import
        from .__about__ import __version__
        from .utils import PluginJSONEncoder

        log.info("{label} {version} is ready.".format(label=self.label, version=__version__))
        log.info(
            "{label} found the following Django signals: {signals}".format(
                label=self.label,
                signals=json.dumps(OPENEDX_SIGNALS, cls=PluginJSONEncoder, indent=4),
            )
        )
        IS_READY = True
