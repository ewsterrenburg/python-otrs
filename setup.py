#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import find_packages
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='python-otrs',
    version='0.4.0',
    description='A programmatic interface to OTRS SOAP API.',
    long_description=README,
    author='Erwin Sterrenburg',
    author_email='e.w.sterrenburg@gmail.com',
    url='https://github.com/ewsterrenburg/python-otrs',
    license='GPLv3',
    zip_safe=False,
    packages=find_packages(),
    install_requires=['defusedxml'],
    include_package_data=True,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    keywords='otrs ticket support soap interface helpdesk',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Natural Language :: English',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Bug Tracking',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ], )
