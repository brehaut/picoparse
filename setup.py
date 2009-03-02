#!/usr/bin/env python

from distutils.core import setup

setup(name='picoparse',
      version='0.9',
      description='Very small parser library for constructing parsers straight forward, and without regular expression',
      author='Andrew Brehaut, Steven Ashley',
      author_email='andrew@brehaut.net',
      url='http://github.com/brehaut/picoparse/',
      packages={'picoparse':'lib'},
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
      ],
     )