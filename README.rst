``linesman`` is a much needed profiler-for-WSGI applications.  It installs as
middleware, can be configured entirely from any ``paster`` config, and aims to
be a jack of all trades when it comes to profiling.

What?
=====

``linesman`` is a name given to people who inspect electrical ``Pylons``, and
was a meek attempt at having a relevant library name.  At the very least, no
library exists with that name--so I'd consider it a win.

The purpose of this project is to provide a tool that can be used to profile an
interactive WSGI application without interrupting workflow, visualizing your
profiling data, and give a dynamic, configurable interface for filtering out
cluttered information.

Reasoning behind writing this library
=====================================

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
