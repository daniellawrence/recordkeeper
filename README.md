recordkeeper
============

A key-value store that is for cli users and software.

[![Build Status](https://travis-ci.org/daniellawrence/recordkeeper.png?branch=master)](https://travis-ci.org/daniellawrence/recordkeeper)

install
--------

    $ virtualenv recordkeeper
    $ recordkeeper/bin/activate
    $ mkdir ~/git
    $ git clone git://github.com/daniellawrence/recordkeeper.git
    $ cd recordkeeper
    $ pip install -r requirements.txt
    $ ./setup.py install
    $ sudo apt-get install mongodb

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




    
