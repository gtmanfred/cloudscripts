# -*- coding: utf-8 -*-
from __future__ import absolute_import
try:
    from urllib.parse import quote as urlquote
except ImportError as exc:
    from urllib import quote as urlquote

from .auth import Auth

short_names = {
    'arch': 'Arch 2015.7 (PVHVM)',
    'centos6': 'CentOS 6 (PVHVM)',
    'centos7': 'CentOS 7 (PVHVM)',
    'coreos-alpha': 'CoreOS (Alpha)',
    'coreos-beta': 'CoreOS (Beta)',
    'coreos-stable': 'CoreOS (Stable)',
    'debian7': 'Debian 7 (Wheezy) (PVHVM)',
    'debian8': 'Debian 8 (Jessie) (PVHVM)',
    'debian-testing': 'Debian Testing (Stretch) (PVHVM)',
    'debian-unstable': 'Debian Unstable (Sid) (PVHVM)',
    'fedora21': 'Fedora 21 (PVHVM)',
    'fedora22': 'Fedora 22 (PVHVM)',
    'freebsd': 'FreeBSD 10 (PVHVM)',
    'gentoo': 'Gentoo 15.3 (PVHVM)',
    'onmetal-centos6': 'OnMetal - CentOS 6',
    'onmetal-centos7': 'OnMetal - CentOS 7',
    'onmetal-coreos-alpha': 'OnMetal - CoreOS (Alpha)',
    'onmetal-coreos-beta': 'OnMetal - CoreOS (Beta)',
    'onmetal-coreos-stable': 'OnMetal - CoreOS (Stable)',
    'onmetal-debian7': 'OnMetal - Debian 7 (Wheezy)',
    'onmetal-debian8': 'OnMetal - Debian 8 (Jessie)',
    'onmetal-debian-testing': 'OnMetal - Debian Testing (Stretch)',
    'onmetal-debian-unstable': 'OnMetal - Debian Unstable (Sid)',
    'onmetal-fedora21': 'OnMetal - Fedora 21',
    'onmetal-fedora22': 'OnMetal - Fedora 22',
    'onmetal-ubuntu1204': 'OnMetal - Ubuntu 12.04 LTS (Precise Pangolin)',
    'omnetal-ubuntu1404': 'OnMetal - Ubuntu 14.04 LTS (Trusty Tahr)',
    'onmetal-ubuntu1504': 'OnMetal - Ubuntu 15.04 (Vivid Vervet)',
    'opensuse': 'OpenSUSE 13.2 (PVHVM)',
    'rhel6': 'Red Hat Enterprise Linux 6 (PVHVM)',
    'rhel7': 'Red Hat Enterprise Linux 7 (PVHVM)',
    'sl6': 'Scientific Linux 6 (PVHVM)',
    'sl7': 'Scientific Linux 7 (PVHVM)',
    'ubuntu1204': 'Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)',
    'ubuntu1404': 'Ubuntu 14.04 LTS (Trusty Tahr) (PVHVM)',
    'ubuntu1504': 'Ubuntu 15.04 (Vivid Vervet) (PVHVM)',
}


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

    def get_image_by_name(self, name=None):
        if name is None:
            imagename = ''
        else:
            imagename = short_names.get(name, name)

        resp = self.sess.get(
            '{publicURL}/images?name={name}'.format(
                name=urlquote(imagename),
                **self.endpoint
            )
        ).json()
        for image in resp.get('images', []):
            if image['name'] == imagename:
                return image['id']
