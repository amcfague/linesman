======================
Linesman Documentation
======================

``linesman`` is a profiler for WSGI applications.  It installs as middleware,
can be configured entirely from any ``paster`` config, and aims to be a
jack-of-all-trades when it comes to profiling WSGI apps.

Unfortunately, there are only a few profilers available for Python, with the
fastest and generally most popular one being `cProfile`.  However, the
output can be very difficult to analyze without having substantial knowledge
about what's going on in an application, which makes it difficult to use.

There are a few select profile wrappers out there--`repoze.profile`,
`keas.profile`, and `dozer` (which is still in alpha) all come to mind, but all
either wrap the output from `cProfile` itself, or show incomplete information.
`Linesman` aims to right this wrong.

.. warning::

    As with most middleware, `linesman` is *not* compatible with ``mod_wsgi``
    in a multi-process environment due to the shared nature between processes.
    Running ``mod_wsgi`` with a single process should work, however.

Overview
--------

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
