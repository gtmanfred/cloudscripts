# -*- coding: utf-8 -*-
from __future__ import absolute_import
from .auth import Auth


class Images(Auth):
    """
    Class for getting information about cloud images

    http://docs.rackspace.com/images/api/v2/ci-devguide/content/ch_image_preface.html
    """
    def __init__(self, username, region, apikey=None, password=None):
        super(Images, self).__init__(username, region.upper(), apikey,
                                     password, endname='cloudImages')

    @property
    def images(self):
        return self.sess.get(
            '{publicURL}/images'.format(**self.endpoint)
        ).json()
