# coding=utf-8
"""
written by:     Lawrence McDaniel
                https://lawrencemcdaniel.com

date:           feb-2022

usage:          listen for Django Signals published by Open edX
                see https://docs.djangoproject.com/en/4.1/topics/signals/
"""
import json
import logging
from attr import asdict

from .utils import serialize_course_key, PluginJSONEncoder, masked_dict
from .waffle import waffle_switches, SIGNALS


log = logging.getLogger(__name__)
log.info("cookiecutter_plugin.signals loaded")


def signals_enabled() -> bool:
    try:
        return waffle_switches[SIGNALS]
    except Exception:  # noqa: B902
        # to resolve a race condition during application launch.
        # the waffle_switches are inspected before the db service
        # has initialized.
        return False


"""
-------------------------------------------------------------------------------
--------------------------- NEW STYLE OF RECEIVER -----------------------------
-------------------- https://github.com/openedx/openedx-events ----------------
-------------------------------------------------------------------------------

    Reference:  edx-platform/docs/guides/hooks/
                https://github.com/openedx/openedx-events

    I scaffolded these from https://github.com/eduNEXT/openedx-events-2-zapier

"""


def certificate_created(certificate, **kwargs):
    """
    see apps.py plugin_app["signals_config"]["lms.djangoapp"]["receivers"]
    signal_path: openedx_events.learning.signals.COURSE_UNENROLLMENT_COMPLETED
    https://github.com/openedx/openedx-events/blob/main/openedx_events/learning/signals.py#L85

    event_type: org.openedx.learning.certificate.created.v1
    event_name: CERTIFICATE_CREATED
    event_description: emitted when the user's certificate creation process is completed.
    event_data: CertificateData

    """
    if not signals_enabled():
        return

    certificate_info = asdict(
        certificate,
        value_serializer=serialize_course_key,
    )
    event_metadata = asdict(kwargs.get("metadata"))
    payload = {
        "certificate": certificate_info,
        "event_metadata": event_metadata,
    }

    log.info(
        "cookiecutter_plugin received CERTIFICATE_CREATED signal for {payload}".format(
            payload=json.dumps(masked_dict(payload), cls=PluginJSONEncoder, indent=4)
        )
    )


def certificate_changed(certificate, **kwargs):
    """
    see apps.py plugin_app["signals_config"]["lms.djangoapp"]["receivers"]
    signal_path: openedx_events.learning.signals.CERTIFICATE_CHANGED
    https://github.com/openedx/openedx-events/blob/main/openedx_events/learning/signals.py#L97

    event_type: org.openedx.learning.certificate.changed.v1
    event_name: CERTIFICATE_CHANGED
    event_description: emitted when the user's certificate update process is completed.
    event_data: CertificateData
    """
    if not signals_enabled():
        return

    certificate_info = asdict(
        certificate,
        value_serializer=serialize_course_key,
    )
    event_metadata = asdict(kwargs.get("metadata"))
    payload = {
        "certificate": certificate_info,
        "event_metadata": event_metadata,
    }

    log.info(
        "cookiecutter_plugin received CERTIFICATE_CHANGED signal for {payload}".format(
            payload=json.dumps(masked_dict(payload), cls=PluginJSONEncoder, indent=4)
        )
    )


def certificate_revoked(certificate, **kwargs):
    """

    see apps.py plugin_app["signals_config"]["lms.djangoapp"]["receivers"]
    signal_path: openedx_events.learning.signals.CERTIFICATE_REVOKED
    https://github.com/openedx/openedx-events/blob/main/openedx_events/learning/signals.py#L109

    event_type: org.openedx.learning.certificate.revoked.v1
    event_name: CERTIFICATE_REVOKED
    event_description: emitted when the user's certificate annulation process is completed.
    event_data: CertificateData
    """
    if not signals_enabled():
        return

    certificate_info = asdict(
        certificate,
        value_serializer=serialize_course_key,
    )
    event_metadata = asdict(kwargs.get("metadata"))
    payload = {
        "certificate": certificate_info,
        "event_metadata": event_metadata,
    }

    log.info(
        "cookiecutter_plugin received CERTIFICATE_REVOKED signal for {payload}".format(
            payload=json.dumps(masked_dict(payload), cls=PluginJSONEncoder, indent=4)
        )
    )

