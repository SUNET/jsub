#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

version = '0.0.1'

install_requires = [
      'redis',
      'inotify'
]

setup(name='jsub',
      version=version,
      description="redis pubsub client",
      long_description=README,
      classifiers=[
          # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      ],
      keywords='redis pubsub',
      author='Leif Johansson',
      author_email='leifj@sunet.se',
      url='http://blogs.mnt.se',
      license='BSD',
      setup_requires=['nose>=1.0'],
      tests_require=['nose>=1.0', 'mock'],
      test_suite="nose.collector",
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
          'console_scripts': ['jsub=jsub:main','jsub-run=jsub.run:main','jsub-send=jsub.send:main']
      },
      message_extractors={'.': [
          ('**.py', 'python', None),
      ]},
)
