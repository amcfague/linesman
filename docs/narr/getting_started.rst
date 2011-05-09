.. _getting started:

Getting Started
===============

This document will cover setting up Linesman in your WSGI application.

Installing Linesman
-------------------

To install the **latest stable version of Linesman**, you can use::

    $ easy_install -U linesman

To install Linesman **from source**, you will need to clone the repository and
run::

    $ python setup.py install

This will install Linesman into `site-packages` and make it available to all
other Python scripts.  No other setup is required.

Setting up middleware
---------------------

Via Configuration (Paster)
^^^^^^^^^^^^^^^^^^^^^^^^^^

Now, you'll need to tell your WSGI application how to use Linesman.  Assuming
you're using Paster, you can do this very easily in your `development.ini` (or
similar) config file.  Add a new filter section::

    [filter:linesman]
    use = egg:linesman#profiler

Then, find the section for your specific application.  Typically, it will have
a section header that looks like ``[app:main]``.  Add the following config
option somewhere within this section::

    filter-with = linesman

Voila!  Once you start your paster server, you'll be all set.  Verify that all
is working correctly by accessing pages on your server.  This will also create
profile entries for the next step.

.. _configuration_code:

Via Code
^^^^^^^^

This requires manually wrapping the WSGI calls in the middleware.  This is only
recommended if you are unable to setup a filter.  Before beginning, please
check your respective WSGI server documentation to see if running your app
through Paster is possible (i.e., `gunicorn
<http://gunicorn.org/run.html#gunicorn-paster>`_), as this requires zero code
changes.

First off, you'll have to open up the area where your app declares middleware.
Typically, this will just be called `app`, but it is heavily dependant on the
framework.  Pylons creates the application in `<project>/config/middleware.py`.

Then, you can create the middleware by passing in the app to the middleware
constructor, like so::

    from linesman.middleware import make_linesman_middleware

    [...]

    app = make_linesman_middleware(app)
    # Or, if you have config options...
    # app = make_linesman_middleware(app, profiler_path="/__profiler")

For a complete list of configurable parameters, please see the
:ref:`configuration` documentation.

Accessing the profiles
----------------------

This will assume that your application is mounted at the root directory,
:file:`/`, and that your server is running on `localhost` at port 5000.  If
not, make sure you adjust your URLs accordingly.

Access the URL at http://127.0.0.1:5000/__profiler__, which should present
you with a list of profiles and times, with a link to the `stats` page.  If you
can see this (and view the profiles), then you're all set!

Happy profiling!
