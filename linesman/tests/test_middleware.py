import os
import tempfile
import uuid
from cProfile import Profile
from unittest import TestCase

from mock import Mock, patch
from nose.tools import assert_equals, raises
from paste.urlmap import URLMap
from webtest import TestApp

import linesman.middleware
from linesman.tests import get_temporary_filename


try:
    # Python 2.7+
    from collections import OrderedDict
except ImportError:
    # Python 2.4+
    from ordereddict import OrderedDict


def generate_profiler_entry():
    def func():
        a = 1 + 2
        return a

    prof = Profile()
    prof.runctx("func()", locals(), globals())
    return prof.getstats()


class TestProfilingMiddleware(TestCase):

    @patch("os.path.exists", Mock(return_value=False))
    @patch("os.makedirs")
    def test_graph_dir_creation(self, mock_makedirs):
        """ Test that the graph dir gets created if it doesn't exist """
        pm = linesman.middleware.ProfilingMiddleware("app")
        mock_makedirs.assert_called_once_with(linesman.middleware.GRAPH_DIR)

    @patch("os.path.exists", Mock(return_value=False))
    @patch("os.makedirs", Mock(side_effect=IOError()))
    @raises(IOError)
    def test_graph_dir_error(self):
        """ Test that not being able to write fails """
        pm = linesman.middleware.ProfilingMiddleware("app")

    def test_middleware_app_non_profiler(self):
        temp_filename = get_temporary_filename()
        profiler_path = "/__profiler__"
        try:
            # Use a sample WSGI app
            map_app = URLMap()
            pm = linesman.middleware.ProfilingMiddleware(
                                        map_app,
                                        profiler_path=profiler_path)
            app = TestApp(pm)
            app.get("/not/profiled/url", status=404)
        finally:
            # Clean up after ourselves
            try:
                os.remove(temp_filename)
            except: pass


    def test_middleware_app_profiler(self):
        temp_filename = get_temporary_filename()
        profiler_path = "/__profiler__"
        try:
            pm = linesman.middleware.ProfilingMiddleware(
                                        Mock(),
                                        profiler_path=profiler_path)
            session = linesman.ProfilingSession(generate_profiler_entry())
            pm._backend.add(session)

            app = TestApp(pm)

            # Test that invalid URLs fail
            app.get('/__profiler__/notaurl', status=404)
            app.get('/__profiler__/graph/notavalidgraph', status=404)
            app.get('/__profiler__/media/js/notafile', status=404)
            app.get('/__profiler__/profiles/notavaliduuids', status=404)

            app.get('/__profiler__/media/js/accordian.js')
            app.get('/__profiler__/profiles/%s' % session.uuid)
            resp = app.get('/__profiler__')
            assert(session.uuid in resp.body)
        finally:
            # Clean up after ourselves
            try:
                os.remove(temp_filename)
            except: pass
