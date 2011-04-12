======================
Linesman Documentation
======================

``linesman`` is a profiler for WSGI applications.  It installs as middleware,
can be configured entirely from any ``paster`` config, and aims to be a
jack-of-all-trades when it comes to profiling WSGI apps.

.. warning::

   As with most plug-ins, this is *not* compatible with ``mod_wsgi`` due to it's
   multi-process nature.  It is compatible with ``paster`` only!

This is the central hub for *all* Linesman documentation.  It covers:

    - instructions on how to setup middleware
    - how to view the on-the-fly graphs and statistics

Things it *does not cover* are:

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
