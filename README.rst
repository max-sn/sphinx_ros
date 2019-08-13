sphinx_ros
==========

.. image:: https://img.shields.io/pypi/v/sphinx-ros
  :target: https://pypi.org/project/sphinx-ros/
  :alt: PyPi version

.. image:: https://img.shields.io/pypi/dm/sphinx-ros
  :target: https://pypi.org/project/sphinx-ros/
  :alt: PyPi downloads per month

.. image:: https://img.shields.io/readthedocs/sphinx-ros/latest
  :target: https://sphinx-ros.readthedocs.io/en/latest/
  :alt: Documentation Status

.. image:: https://img.shields.io/badge/buy%20me%20a%20coffee-3%24-blue
  :target: https://paypal.me/maxsn0/3USD
  :alt: Buy me a coffee

This extension adds reStructuredText directives that can be used to document
ROS packages.

Usage
-----

Include the extension in your ``conf.py`` file. If you have no extensions yet,
use::

  extensions = ['sphinx_ros']

Otherwise use::

  extensions.append('sphinx_ros')

This adds the ``ros`` domain to `Sphinx <http://www.sphinx-doc.org/>`_, and
allows you to use the directives defined in this extension, e.g. 
``.. ros:package::``, ``.. ros:message::`` et cetera.

A minimal example::

  .. ros:package:: foo_bar_package

  .. ros:message:: foo
  
    :msg_param bar: The bar included in foo.
    :msg_paramtype bar: :ros:msg:`int16`

See `the docs <http://sphinx-ros.readthedocs.io>`_ for more information.
