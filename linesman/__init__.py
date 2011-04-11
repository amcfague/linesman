from inspect import getmodule
from tempfile import gettempdir
import logging
import networkx as nx
import os
import uuid

log = logging.getLogger(__name__)


def draw_graph(graph, output_path):
    nx.to_agraph(graph).draw(output_path, prog="dot")
    log.info("Wrote output to `%s'" % output_path)
    return output_path

class ProfilingSession(object):

    def __init__(self, stats, environ={}, timestamp=None):
        self._graph = None
        self._uuid = uuid.uuid1()

        # Save some environment variables (if available)
        self.path = environ.get('PATH_INFO')

        # Some profiling session attributes need to be calculated
        self.duration = max([stat.totaltime for stat in stats])
        self.cutoff_percentage = 0.1
        self.cutoff_time = self.duration * self.cutoff_percentage
        self.timestamp = timestamp

        self._create_graph(stats)

    def _create_graph(self, stats):
        def generate_key(stat):
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

        # Create a graph; dot graphs need names, so just use `G' so that
        # pygraphviz doesn't complain when we render it.
        g = nx.DiGraph(name="G")

        # Iterate through stats to add the original nodes.  The will add ALL
        # the nodes, even ones which might be pruned later.  This is so that
        # the library will always have the original callgraph, which can be
        # manipulated for display purposes later.
        for stat in stats:
            caller_key = generate_key(stat)

            attrs = {
                'callcount': stat.callcount,
                'inlinetime': stat.inlinetime,
                'reccallcount': stat.reccallcount,
                'totaltime': stat.totaltime,
            }
            g.add_node(caller_key, attr_dict=attrs)

            # Add all the calls as edges
            for call in stat.calls or []:
                callee_key = generate_key(call)

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

        self._graph = g

    @property
    def uuid(self):
        return str(self._uuid)
