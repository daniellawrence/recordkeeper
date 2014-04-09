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
      'bin/rk_delete.py','bin/rk_new.py','bin/rk_print.py',
      'bin/rk_update.py','bin/start_webserver.py'],
      #requires=open('requirements.txt').readlines()
)
