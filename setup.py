#!/usr/bin/env python
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from linkedin import __version__


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    long_description = readme.read()

setup(name='python-linkedin',
      version=__version__,
      description='Python Interface to the LinkedIn API',
      long_description=long_description,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Natural Language :: English',
      ],
      keywords='linkedin python',
      author='Ozgur Vatansever',
      author_email='ozgurvt@gmail.com',
      maintainer='Ozgur Vatansever',
      maintainer_email='ozgurvt@gmail.com',
      url='http://ozgur.github.com/python-linkedin/',
      license='MIT',
      packages=['linkedin'],
      install_requires=['requests>=1.1.0', 'requests-oauthlib>=0.3'],
      zip_safe=False
)
