#!/usr/bin/env python
import setuptools

setuptools.setup(
    name='cloudlibs',
    version='0.0.1',
    description='Rackspace cloud api scripts',
    author='Daniel Wallace',
    author_email='danielwallace@gtmanfred.com',
    entry_points={
        'console_scripts': [
            'rcv3=scripts.rcv3:main'
        ]
    },
    packages=['cloudlibs'],
    zip_safe=False
)
