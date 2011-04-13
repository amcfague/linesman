from mock import Mock, patch
from unittest import TestCase
import linesman

class TestProfilingMiddleware(TestCase):

    @patch("os.path.exists", Mock(return_value=False))
    @patch("os.makedirs")
    def test_graph_dir_creation(self, mock_makedirs):
        """ Test that the graph dir gets created if it doesn't exist """
        pm = linesman.ProfilingMiddleware("app")
        mock_makedirs.assert_called_once_with(linesman.middleware.GRAPH_DIR)
