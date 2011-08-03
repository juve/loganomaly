import os
import sys

import ez_setup
ez_setup.use_setuptools('0.6c11')

from setuptools import setup, find_packages

from loganomaly import __version__

setup(
    name = "loganomaly",
    version = __version__,
    author = "Gideon Juve",
    author_email = "gideonjuve@gmail.com",
    description = ("Similar to logwatch"),
    license = "Apache License, Version 2.0",
    keywords = "log monitoring anomaly detection",
    url = "http://www.isi.edu/~gideon",
    install_requires = [
    ],
    packages = find_packages(),
    scripts = ['bin/loganomaly'],
    long_description = "",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python'
    ],
)
