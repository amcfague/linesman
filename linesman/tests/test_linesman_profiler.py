from cProfile import Profile
from mock import Mock, patch
from nose.tools import assert_equals
import linesman
import unittest

def generate_profiler_entry():
    def func():
        a = 1 + 2
        return a

    prof = Profile()
    prof.runctx("func()", locals(), globals())
    return prof.getstats()

class TestProfilingSession(unittest.TestCase):

    def setUp(self):
        self.stats = generate_profiler_entry()

    @patch("linesman.create_graph")
    def test_init_default_args(self, mock_create_graph):
        """ Test ProfilingSession initialization with default args """
        session = linesman.ProfilingSession(self.stats)
        mock_create_graph.assert_called_with(self.stats)
        assert_equals(session.path, None)
        assert_equals(session.timestamp, None)
        assert_equals(str(session._uuid), session.uuid)

    @patch("linesman.create_graph")
    def test_init_environ(self, mock_create_graph):
        """ Test ProfilingSession initialization with an environ args """
        environ = {'PATH_INFO': '/some/path'}
        session = linesman.ProfilingSession(self.stats, environ)
        mock_create_graph.assert_called_with(self.stats)
        assert_equals(session.path, environ.get('PATH_INFO'))
        assert_equals(session.timestamp, None)
        assert_equals(str(session._uuid), session.uuid)

    @patch("linesman.create_graph")
    def test_init_environ_timestamp(self, mock_create_graph):
        """ Test ProfilingSession initialization with all args """
        environ = {'PATH_INFO': '/some/path'}
        timestamp = "Some generic timestamp"
        session = linesman.ProfilingSession(self.stats, environ, timestamp)
        mock_create_graph.assert_called_with(self.stats)
        assert_equals(session.path, environ.get('PATH_INFO'))
        assert_equals(session.timestamp, timestamp)
        assert_equals(str(session._uuid), session.uuid)
