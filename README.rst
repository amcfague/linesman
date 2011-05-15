``linesman`` is a much needed profiler-for-WSGI applications.  It installs as
middleware, can be configured entirely from any ``paster`` config, and aims to
be a jack-of-all-trades when it comes to profiling WSGI apps.

Since a picture is worth a thousand words, here are a few screenshots of the
interface:

- `Session listing
  <https://github.com/amcfague/linesman/raw/master/examples/session_listing.png>`_
- `Profile page
  <https://github.com/amcfague/linesman/raw/master/examples/profile.png>`_
- `Profile page w/ pie chart
  <https://github.com/amcfague/linesman/raw/master/examples/profile-with-pie-chart.png>`_
- `Generated callgraph
  <https://github.com/amcfague/linesman/raw/master/examples/callgraph.png>`_

The changelog can always be viewed `from the source
<https://github.com/amcfague/linesman/blob/master/docs/changelog.rst>`_, or `on
PyPi <http://packages.python.org/linesman/changelog.html>`_.  Keep in mind,
PyPi is only updated with each release, and does not include development
documentation.

Reasoning behind this library
=============================

One of my team's stories at work was to investigate existing Python profiling
tools for use with some of our new web stacks (all in Pylons).  I looked at a
few--``repoze.profile``, ``kea.profile``, and even ``dozer`` (still in
0.2alpha)--but couldn't find any that suited our use case.  We wanted to...

- visualize the flow of our code
- identify bottlenecks quickly and easily
- have the ability to strip out extraneous calls

Many of the tools simply outputted the ``pstats`` object from ``cProfile``,
which can be difficult to parse, and even more difficult to identify the call
order.  Considering that ``cProfile`` provided all the information needed, I
figured it would be just as easy to write our own middleware.

``linesman`` is a name given to people who inspect electrical ``Pylons``, and
was a meek attempt at having a relevant library name.

Setting up middleware
=====================

Now, you'll need to tell your WSGI application how to use Linesman.  Assuming
you're using Paster, you can do this very easily in your `development.ini` (or
similar) config file.  Add a new filter section::

    [filter:linesman]
    use = egg:linesman#profiler

Then, find the section for your specific application.  Typically, it will have
a section header that looks like ``[app:main]``.  Add the following config
option somewhere within this section::

    filter-with = linesman

Wallah!  Once you start your paster server, you'll be all set.  Verify that all
is working correctly by accessing pages on your server.  This will also create
profile entries for the next step.

Accessing the profiles
======================

This will assume that your application is mounted at the root directory,
`/`, and that your server is running on `localhost` at port 5000.  If
not, make sure you adjust your URLs accordingly.

Access the URL at http://127.0.0.1:5000/__profiler__, which should present
you with a list of profiles and times, with a link to the `stats` page.  If you
can see this (and view the profiles), then you're all set!

Happy profiling!
