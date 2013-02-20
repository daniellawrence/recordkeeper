recordkeeper
============

A key-value store that is for cli users and software.

[![Build Status](https://travis-ci.org/daniellawrence/recordkeeper.png?branch=master)](https://travis-ci.org/daniellawrence/recordkeeper)

pre-install:mongodb
-------------------

Install mongodb on your database server ( could be the same system. )
    $ sudo apt-get install mongodb
If mongodb is not installed on the same system as recordkeeper then you need to 
adjust the bind_ip in /etc/mongodb.conf
    $ sudo vi  /etc/mongodb.conf
    bind_ip = 0.0.0.0
    $ sudo service mongodb restart

pre-install:pymongo
--------------------

In order for pymongo to compile from the pip install you need to have the python-dev
packages installed on your system.
    $ sudo apt-get install python-dev

install:recordkeeper
---------------------

Create a new virtual env for recordkeeper
    $ virtualenv ~/virtualenv/recordkeeper
Activate it.
    $ ~/virtualenv/recordkeeper/bin/activate
Clone the repo
    $ mkdir ~/git
    $ git clone git://github.com/daniellawrence/recordkeeper.git
Install the requirements
    $ cd recordkeeper
    $ pip install -r requirements.txt
Install recordkeeper!
    $ ./setup.py install


setup
---------------------
If monogdb has been installed on a different server, then you need to create a 
local_settings.py to let recordkeeper know where to find its database.

    $ echo "DATABASE_HOST = YOUR-SERVER-IP" > ~/git/recordkeeper/recordkeeper/local_settings.py

start
-----

    $ cd ~/git/recordkeeper
    $ tests/querytest.py

examples
--------

    $ cd ~/git/recordkeeper/bin

Query the test data

    $ ./rk_print.py name age=3
    sandy
    bob
    greg

Customize output

    $ ./rk_print.py name age=3 age
    sandy 3
    bob 3
    greg 3

Greater than operator

    $ ./rk_print.py name age.gt.2 age
    sandy 3
    bob 3
    greg 3

simple regex

    $ ./rk_print.py name~o name
    bob
    john




    
