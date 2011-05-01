Configuring Linesman
====================

Configuration of ``linesman`` is done through the controlling process, such as
Paster.  Thus, this assumes that the configuration is similar to the
instructions given in the :ref:`getting started` documentation. ::

    [filter:linesman]
    use = egg:linesman#profiler

All options can be made under this section.

Configuring the Middleware
--------------------------

``profiler_path``
"""""""""""""""""

This is a path relative to the root of your webapp that can be used to access
the profiler.  For example, if the host is being run on ``localhost:5000``, and
the application is mounted on the ``/`` context, then specifying a
``profiler_path`` of ``__profiler__`` will use ``localhost:5000/__profiler__``.

Consequently, if the same application is NOT mounted under the root context,
and is instead mounted at ``/webapp``, the same ``profiler_path`` would match
``localhost:5000/webapp/__profiler__``.

``backend``
"""""""""""
Takes the form of :samp:`{module}:{class_or_function}`, where
`class_or_function` resolves to a class that implements
:class:`~linesman.backends.Backend`.  To see which backends are available, take
a look at the :mod:`~linesman.backends` modules.

Additionally, you can specify _any_ module, regardless of rather or not its
distributed with Linesman.

Configuring the Backends
------------------------

Whatever ``backend`` is set to, there are new sets of config values that can be
used.  This data differs depending on the plug-in, so in order to always keep
the documentation up-to-date, visit the :mod:`linesman.backends` page.
Whatever values :func:`__init__` accepts are values that can be passed in
through the configuration file.

For example, :class:`~linesman.backends.pickle.PickleBackend` defines a
``filename`` parameter.  Thus, to set the Pickle filename, use the following
config parameter::

    filename = sessions.dat

Remember, always use the backends page for the most up-to-date info.
