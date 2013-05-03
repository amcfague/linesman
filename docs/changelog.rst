0.3.1 (2013-05-02)
------------------

:Contributor: Gert Berger

* Add delete_many to delete multiple selected sessions at once. (GertBerger)

0.3.0 (2013-03-12)
------------------

:Contributor: Gert Burger
:Contributor: Sam Kimbrel
:Contributor: J.J. Guy

* Use pillow instead of PIL. (GertBerger)
* WebOb requires that response.text is a unicode object. (GertBerger)
* Fix a couple resp.text unicode issues (skimbrel)
* Fix timezone-dependent test (skimbrel)
* Assign unicode template to body_unicode (jjguy)

0.2.3 (2013-01-16)
------------------

:Contributor: Hong Minhee
:Contributor: Sam Kimbrel

* linesman updated to support webob>=1.2 (dahlia, skimbrel)

0.2.2 (2011-09-30)
------------------
:Contributor: Calen Pennington

Bugs
^^^^

* Date sorting logic was not correct.  (cpennington)

0.2.1 (2011-08-25)
------------------

:Contributor: Luis Peralta

Bugs
^^^^

* os.abspath should have been os.path.abspath (lperalta)
* Updated unittests back to 100% to catch errors, such as the one lperalta
  found.

0.2 (2011-05-14)
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
