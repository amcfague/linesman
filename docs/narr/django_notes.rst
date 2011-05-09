Django notes
============

The Problem
-----------

Unfortunately, Django uses the term `middleware` incorrect.  What it refers to
is, specifically, `Django middleware`.  WSGI middleware, on the otherhand, is
defined by :pep:`333` and is warranted as a standard that all WSGI servers
follow.

Possible Solutions
------------------

Currently, `linesman` can *only* be run in a WSGI environment that adheres to
:pep:`333`, as mentioned above.  If this is the case, you can wrap the
application call by following the instructions in :ref:`configuration_code`.
For example, the official Django docs refer to using `mod_wsgi and Apache to
host a Django app
<http://docs.djangoproject.com/en/dev/howto/deployment/modwsgi/>`_.  In this
case, you would wrap the :meth:`django.core.handlers.wsgi.WSGIHandler()` call
with the middleware, like so::

    import os
    import sys

    os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

    import django.core.handlers.wsgi
    from linesman.middleware import make_linesman_middleware
    application = django.core.handlers.wsgi.WSGIHandler()
    application = make_linesman_middleware(application)

If running a full WSGI server is a little too heavy-weight, there's a very,
very alpha release of `DjangoPaste <http://pypi.python.org/pypi/DjangoPaste>`_,
which provides the ability to launch Django using Paste.

The final solution (not yet implemented) is to wrap the middleware so that it is usuable by the
Django middleware.  This introduces two big issues.  First, when implemented as
WSGI middleware, `linesman` can wrap the *whole* request, from start to finish.
With Django, the profiling will only begin when Django initializes the
middleware.  Secondly, because I am not familiar with Django (yet), it may not
be possible to simply jury rig the middleware onto a request.  But this may be
changed after future research.

Conclusion (tl;dr)
------------------

If your Django app is being run in a WSGI environment, you do not need to do
any additional work and can wrap the application by following the instructions
on the :ref:`getting started page <configuration_code>`.  Otherwise, there's no
convenient or easy solution for running `linesman` on Django.
