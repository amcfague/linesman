# This file is part of linesman.
#
# linesman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# linesman is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with linesman.  If not, see <http://www.gnu.org/licenses/>.
#
import logging
import uuid
from inspect import getmodule

import networkx as nx


log = logging.getLogger(__name__)


def _generate_key(stat):
    code = stat.code

    # First, check if its built-in (i.e., code is a string)
    if isinstance(code, str):
        return code

    # If we have a module, generate the module name (a.b.c, etc..)
    module = getmodule(code)
    if module:
        return ".".join((module.__name__, code.co_name))

    # Otherwise, return a path based on the filename and function name.
    return "%s.%s" % (code.co_filename, code.co_name)


def draw_graph(graph, output_path):
    """
    Draws a networkx graph to disk using the `dot` format.

    ``graph``:
        networkx graph
    ``output_path``:
        Location to store the rendered output.
    """
    nx.to_agraph(graph).draw(output_path, prog="dot")
    log.info("Wrote output to `%s'" % output_path)


def create_graph(stats):
    """
    Given an instance of :class:`pstats.Pstats`, this will use the generated
    call data to create a graph using the :mod:`networkx` library.  Node
    and edge information is stored in the graph itself, so that the stats
    object itself--which can't be pickled--does not need to be kept around.

    ``stats``:
        An instance of :class:`pstats.Pstats`, usually retrieved by calling
        :func:`~cProfile.Profile.getstats()` on a cProfile object.

    Returns a :class:`networkx.DiGraph` containing the callgraph.
    """

    # Create a graph; dot graphs need names, so just use `G' so that
    # pygraphviz doesn't complain when we render it.
    g = nx.DiGraph(name="G")

    # Iterate through stats to add the original nodes.  The will add ALL
    # the nodes, even ones which might be pruned later.  This is so that
    # the library will always have the original callgraph, which can be
    # manipulated for display purposes later.
    duration = max([stat.totaltime for stat in stats])

    for stat in stats:
        caller_key = _generate_key(stat)

        attrs = {
            'callcount': stat.callcount,
            'inlinetime': stat.inlinetime,
            'reccallcount': stat.reccallcount,
            'totaltime': stat.totaltime,
        }
        g.add_node(caller_key, attr_dict=attrs)

        # Add all the calls as edges
        for call in stat.calls or []:
            callee_key = _generate_key(call)

            call_attrs = {
                'callcount': call.callcount,
                'inlinetime': call.inlinetime,
                'reccallcount': call.reccallcount,
                'totaltime': call.totaltime,
            }

            # Add the edge using a weight and label
            g.add_edge(caller_key, callee_key,
                       weight=call.totaltime,
                       label=call.totaltime,
                       attr_dict=call_attrs)

    return g


class ProfilingSession(object):
    """
    The profiling session is used to store long-term information about the
    profiled call, including generating the complete callgraph based on
    cProfile's stats output.

    Of special interest is the ``uuid`` that it generates to uniquely track
    this request.

    ``stats``:
        An instance of :class:`pstats.Pstats`, usually retrieved by calling
        :func:`~cProfile.Profile.getstats()` on a cProfile object.
    ``environ``:
        If specified, this Session will store `environ` data.  This should be
        the environment setup by the WSGI server (i.e., :mod:`paster`).
    ``timestamp``:
        If specified, this should mark the beginning of the profiling
        session--i.e., when Profile.run() was called.  This can be any format
        if your choosing; however, the default templates simply invoke
        ``timestamp.__repr__``, so whatever object you use should provide at
        _least_ that function.
    """

    def __init__(self, stats, environ={}, timestamp=None):
        self._graph = None
        self._uuid = uuid.uuid1()

        # Save some environment variables (if available)
        self.path = environ.get('PATH_INFO')

        # Some profiling session attributes need to be calculated
        self.duration = max([stat.totaltime for stat in stats])

        self.timestamp = timestamp

        self._graph = create_graph(stats)

    @property
    def uuid(self):
        """ See :term:`session_uuid`. """
        return str(self._uuid)
