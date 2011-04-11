======================
Linesman Documentation
======================

This is the central hub for _all_ Linesman documentation.  It includes
instructions on how to get your environment setup, and how to monitor usage.
Things it does NOT cover are:

    - interpreting profiling data
    - memory leaks
    - how to improve your application's response time

To **run unittests**::

    # Standard faire
    nosetests

    # With coverage reports
    nosetests --with-coverage --cover-package=linesman

To **build this documentation**::

    $ easy_install sphinx
    [...]
    $ python setup.py build_sphinx

The built documentation is available (by default) in :file:`build/sphinx/html`,
and can be viewed locally on your web browser without the need for a separate
web server.

Narrative Documentation
=======================

.. toctree::
    :maxdepth: 1
    :glob:

    narr/*

Tutorials
=========

.. toctree::
   :maxdepth: 1
   :glob:

   tutorials/*


Reference Material
==================

.. toctree::
   :maxdepth: 2
   :glob:

   api/*

Index and Glossary
==================

* :doc:`glossary`
* :ref:`genindex`
* :ref:`search`
