
# python stuff
import logging
import mimetypes
import requests

# django stuff
from django.conf import settings

# openedx stuff
from lms.djangoapps.badges.backends.badgr import BadgrBackend

LOGGER = logging.getLogger(__name__)


class BadgrBoto3Backend(BadgrBackend):

    def _create_badge(self, badge_class):
        """
        Create the badge class on Badgr.
        """
        image = badge_class.image
        # We don't want to bother validating the file any further than making sure we can detect its MIME type,
        # for HTTP. The Badgr-Server should tell us if there's anything in particular wrong with it.
        content_type, __ = mimetypes.guess_type(image.name)
        if not content_type:
            raise ValueError(
                "Could not determine content-type of image! Make sure it is a properly named .png file. "
                "Filename was: {}".format(image.name)
            )

        # ---------------------------------------------------------------------
        # FIX NOTE: HEY, HEY, HEY!!!! I DON'T WORK!!!!!
        # ---------------------------------------------------------------------
        with open(image.path, 'rb') as image_file:
            files = {'image': (image.name, image_file, content_type)}
            data = {
                'name': badge_class.display_name,
                'criteriaUrl': badge_class.criteria,
                'description': badge_class.description,
            }
            result = requests.post(
                self._badge_create_url, headers=self._get_headers(),
                data=data, files=files, timeout=settings.BADGR_TIMEOUT)
            self._log_if_raised(result, data)
            try:
                result_json = result.json()
                badgr_badge_class = result_json['result'][0]
                badgr_server_slug = badgr_badge_class.get('entityId')
                badge_class.badgr_server_slug = badgr_server_slug
                badge_class.save()
            except Exception as excep:  # pylint: disable=broad-except
                LOGGER.error(
                    'Error on saving Badgr Server Slug of badge_class slug '
                    '"{0}" with response json "{1}" : {2}'.format(
                        badge_class.slug, result.json(), excep))

