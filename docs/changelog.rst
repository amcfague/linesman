0.2 (development)
-----------------

:Contributor: Calen Pennington <cpennington>
:Contributor: Rudd Zwolinski <ruddzw>

.. warning::

    This release will break profile persistence from 0.1.  This is because the
    default backend has been moved to SQLite, which is a *much* faster storage
    mechanism.

Bugs
^^^^

* Requests containing unicode no longer cause errors.
* Row hovering now works in all browsers. (Issue #2)
* Terminology for inlinetime, totaltime changed to match cProfile.

Documentation
^^^^^^^^^^^^^

* Added notes for using Linesman with Django.
* Docstring additions across the board.

Features
^^^^^^^^

* Added ability to enable/disable profiling on-the-fly. (Issue #8)
* All or specific sessions can now be deleted from the session listing. (Issue
  #4)
* Introduced modular backends; now possible to store results in either entirely
  pickled form or in SQLite.
* Pie charts can be used to visually display time spent in specific packages;
  the list of packages is configurable in the middleware. (Issue #1)
* Session history is now displayed in a nice manner (Issue #5)

0.1.1 (2011-05-06)
------------------

Bugs
^^^^

* setuptools will not correctly include data sources unless they live in
  MANIFEST.in.

0.1 (2011-04-29)
----------------

* Initial release
