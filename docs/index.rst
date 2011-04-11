======================
Linesman Documentation
======================

This is the central hub for *all* Linesman documentation.  It covers:

    - instructions on how to setup middleware
    - how to view the on-the-fly graphs and statistics

Things it *does NOT cover* are:

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
