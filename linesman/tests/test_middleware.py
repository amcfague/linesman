from cProfile import Profile
from mock import Mock, patch
from nose.tools import assert_equals, raises
from paste.urlmap import URLMap
from unittest import TestCase
from webtest import TestApp
import cPickle
import linesman
import linesman.middleware
import os
import tempfile
import uuid

def generate_profiler_entry():
    def func():
        a = 1 + 2
        return a

    prof = Profile()
    prof.runctx("func()", locals(), globals())
    return prof.getstats()

def get_temporary_filename():
    fn = str(uuid.uuid1())
    return os.path.join(tempfile.gettempdir(), fn)

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

    @patch("linesman.create_graph", Mock(return_value=None))
    @patch("os.path.exists", Mock(return_value=True))
    def test_pickle_existing_dict(self):
        """ Check that new data in sessions get opened up correctly """
        temp_filename = get_temporary_filename()
        try:
            # Setup a little profiler
            with patch("__builtin__.open", Mock(side_effect=IOError())):
                pm = linesman.middleware.ProfilingMiddleware("app",
                                                session_history_path=temp_filename)
            session = linesman.ProfilingSession(generate_profiler_entry())
            session._graph = {"key": "value"}
            pm._add_session(session)

            # Make sure we can re-open it!
            with open(temp_filename, 'rb') as pickle_fd:
                unpickled_sessions = cPickle.load(pickle_fd)

            # We should be the ONLY item in this session, so make sure we're
            #   the same object.
            assert_equals(1, len(unpickled_sessions))
            assert_equals(session._graph,
                          unpickled_sessions[session.uuid]._graph)
        finally:
            # Clean up after ourselves
            try:
                os.remove(temp_filename)
            except: pass

    @patch("__builtin__.open", Mock(side_effect=IOError()))
    @patch("os.path.exists", Mock(return_value=True))
    def test_pickle_new_dict(self):
        # Setup a little profiler
        temp_filename = get_temporary_filename()
        try:
            pm = linesman.middleware.ProfilingMiddleware("app",
                                            session_history_path=temp_filename)
            assert_equals(linesman.middleware.OrderedDict(), pm._session_history)
        finally:
            # Clean up after ourselves
            try:
                os.remove(temp_filename)
            except: pass

    def test_middleware_app_non_profiler(self):
        temp_filename = get_temporary_filename()
        profiler_path = "/__profiler__"
        try:
            # Use a sample WSGI app
            map_app = URLMap()
            pm = linesman.middleware.ProfilingMiddleware(
                                        map_app,
                                        profiler_path=profiler_path,
                                        session_history_path=temp_filename)
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
                                        profiler_path=profiler_path,
                                        session_history_path=temp_filename)
            session = linesman.ProfilingSession(generate_profiler_entry())
            pm._add_session(session)

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
