# coding=utf-8
"""
written by:     Lawrence McDaniel
                https://lawrencemcdaniel.com

date:           mar-2023

usage:
    resolves a configuration issue with Badgr badges when running Kubernetes.
    see: https://discuss.openedx.org/t/badgr-badging-support/8342

    BadgrBackend._create_badge() assumes that the you are using the Django
    storages default backend of the Ubuntu file system. This will break
    if you instead use the amazon-S3 storages backend, which is a requirement
    for running openedx at scale; not solely Kubernetes, but ANY horizontal
    scaling of the openedx app servers.

    Specifically, this line breaks in the default badges backend:
    https://github.com/openedx/edx-platform/blob/open-release/olive.master/lms/djangoapps/badges/backends/badgr.py#L120

    The cause of this problem is pretty simple
    ------------------------------------------
    1. the attribute value image.path is populated automatically in get_completion_badge() -
       see https://github.com/openedx/edx-platform/blob/open-release/olive.master/lms/djangoapps/badges/events/course_complete.py#L84       # noqa: B950
       an example value of image.path is 'badge_classes/course_complete_badges/badge-icon-png-22.png'

    2. the image field itself is defined in models.py as
       image = models.ImageField(upload_to='badge_classes', validators=[validate_badge_image])
       Meanwhile, models.ImageField defines its path property as 'return self.storage.path(self.name)'
       see: https://docs.djangoproject.com/en/2.1/_modules/django/db/models/fields/files/

    3. finally, django-storages amazon-s3 backend does not implement the path property,
       leading to this Exception being raised: NotImplementedError("This backend doesn't support absolute paths.")
       see: https://docs.djangoproject.com/en/4.1/_modules/django/core/files/storage/

    More
    ------------------------------------------
    django-storages amazon-s3 can use either an S3 or a Cloudfront domain address, so we should check for both
    and bias to the Cloudfront domain if its setup.

    An example of the actual location of the same course completion badge when Cloudfront has been enabled is:
        https://cdn.courses.smartlikefox.com/badge_classes/course_complete_badges/badge-icon-png-22.png

    An example of the actual location of the same course completion badge when Cloudfront has not been enabled is:
        https://s3.us-east-1.amazonaws.com/smartlikefox-usa-prod-storage/badge_classes/course_complete_badges/badge-icon-png-22.png
"""

# python stuff
import logging
import requests

# django stuff
from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

# openedx stuff
from lms.djangoapps.badges.backends.badgr import BadgrBackend

log = logging.getLogger(__name__)


class BadgrBoto3Backend(BadgrBackend):
    def __init__(self):
        super().__init__()
        log.info("cookiecutter_plugin.badges.backends.badgr_boto3.BadgrBoto3Backend - ready.")

    def _cookiecutter_boto3_uri(self, filename):
        """
        return a valid awscli URI pointing to the AWS S3 bucket root, preferaby via
        Cloudfront, otherwise via AWS S3 URI.

        examples
            filename:                           badge_classes/course_complete_badges/badge-icon-png-22.png
            settings.AWS_S3_CUSTOM_DOMAIN:      cdn.courses.smartlikefox.com
            settings.AWS_STORAGE_BUCKET_NAME:   smartlikefox-usa-prod-storage
            S3 URI:                             s3://smartlikefox-usa-prod-storage
        """

        try:
            # example: https://cdn.courses.smartlikefox.com/badge_classes/course_complete_badges/badge-icon-png-22.png
            aws_s3_custom_domain = "https://{aws_s3_custom_domain}/{filename}".format(
                aws_s3_custom_domain=settings.AWS_S3_CUSTOM_DOMAIN, filename=filename
            )
            validate = URLValidator()
            validate(aws_s3_custom_domain)
            return aws_s3_custom_domain
        except ValidationError:
            # example: s3://smartlikefox-usa-prod-storage/badge_classes/course_complete_badges/badge-icon-png-22.png
            aws_storage_bucket_name = "s3://{aws_storage_bucket_name}/{filename}".format(
                aws_storage_bucket_name=settings.AWS_STORAGE_BUCKET_NAME, filename=filename
            )
            return aws_storage_bucket_name

    def _create_badge(self, badge_class):
        """
        Create the badge class on Badgr.

        badge_class - badges.BadgeClass(models.Model)
        badge_class.image - models.ImageField(upload_to='badge_classes')
        """
        log.info("cookiecutter_plugin.badges.backends.badgr_boto3._create_badge() - start")
        if badge_class is None or badge_class.image is None:
            log.error("either received None for badge_class or badge_class.image is None")
            return

        image_filename = badge_class.image.name

        boto3_uri = self._cookiecutter_boto3_uri(image_filename)
        response = requests.get(boto3_uri)
        if response.status_code != requests.codes.ok:
            log.error(
                "received {status_code} response on URI {uri}".format(status_code=response.status_code, uri=boto3_uri)
            )
            response.raise_for_status()
            return

        # ---------------------------------------------------------------------
        # mcdaniel: everything following the http response is intended to match
        # the default badges backend exactly.
        # ---------------------------------------------------------------------

        image_content = response.content
        image_content_type = response.headers["content-type"]
        files = {"image": (image_filename, image_content, image_content_type)}
        data = {
            "name": badge_class.display_name,
            "criteriaUrl": badge_class.criteria,
            "description": badge_class.description,
        }
        result = requests.post(
            self._badge_create_url, headers=self._get_headers(), data=data, files=files, timeout=settings.BADGR_TIMEOUT
        )
        self._log_if_raised(result, data)
        try:
            result_json = result.json()
            badgr_badge_class = result_json["result"][0]
            badgr_server_slug = badgr_badge_class.get("entityId")
            badge_class.badgr_server_slug = badgr_server_slug
            badge_class.save()
        except Exception as excep:  # noqa: E902
            log.error(
                "Error on saving Badgr Server Slug of badge_class slug "
                '"{0}" with response json "{1}" : {2}'.format(badge_class.slug, result.json(), excep)
            )

        log.info("cookiecutter_plugin.badges.backends.badgr_boto3._create_badge() - finish")
