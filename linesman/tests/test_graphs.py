from cProfile import Profile
from mock import Mock, patch
from nose.tools import assert_equals
import linesman
import unittest

class TestGraphUtils(unittest.TestCase):

    @patch("networkx.to_agraph")
    def test_draw_graph(self, mock_to_agraph):
        """ Test that the graph gets converted to an agraph """
        mock_draw = Mock()
        mock_to_agraph.return_value = mock_draw

        graph = "some graph object"
        output = "/tmp/somefile.png"
        linesman.draw_graph(graph, output)

        mock_to_agraph.assert_called_with(graph)
        mock_draw.draw.assert_called_with(output, prog="dot")

    def test_generate_key_builtin(self):
        """ Test that a key is generated for built-in functions """
        stat = Mock()
        stat.code = "__builtin__"
        key = linesman._generate_key(stat)
        assert_equals(key, stat.code)

    def test_generate_key_module(self):
        """ Test that a key is generated for module functions """
        def test_func(): pass

        stat = Mock()
        stat.code = test_func.__code__

        expected_key = "%s.%s" % (self.__module__, stat.code.co_name)
        key = linesman._generate_key(stat)
        assert_equals(key, expected_key)

    @patch("linesman.getmodule", Mock(return_value=None))
    def test_generate_key_unknown(self):
        """ Test that unknown module functions return as strings """
        def test_func(): pass

        stat = Mock()
        stat.code = test_func.__code__

        expected_key = "%s.%s" % (stat.code.co_filename, stat.code.co_name)
        key = linesman._generate_key(stat)
        assert_equals(key, expected_key)

    def test_create_graph(self):
        """ Test that a graph gets generated for a test function """
        def test_func(): pass
        prof = Profile()
        prof.runctx("test_func()", locals(), globals())
        graph = linesman.create_graph(prof.getstats())
        
        # We should only ever have three items here
        assert_equals(len(graph), 3)

        # Assert that the three items we have are as expected
        assert_equals(graph.nodes(),
            ['<string>.<module>',
             'linesman.tests.test_graphs.test_func',
             "<method 'disable' of '_lsprof.Profiler' objects>"])

        # Assert that the correct edges are set-up
        assert_equals([('<string>.<module>', 'linesman.tests.test_graphs.test_func')], graph.edges())
