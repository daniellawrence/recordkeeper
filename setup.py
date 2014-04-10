#!/usr/bin/env python

from distutils.core import setup

setup(name='RecordKeeper',
      version='0.0',
      description='RecordKeeper',
      author='Danny Lawrence',
      author_email='dannyla@linux.com',
      url='http://www.github.com/daniellawrence/recordkeeper',
      packages=['recordkeeper'],
      scripts=[
          'bin/rk_delete','bin/rk_new','bin/rk_print',
          'bin/rk_update','bin/start_webserver.py',
          'bin/rk_listkeys'],
      #requires=open('requirements.txt').readlines()
)
