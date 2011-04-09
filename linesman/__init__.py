from inspect import getmodule
from tempfile import gettempdir
import logging
import networkx as nx
import os
import uuid

log = logging.getLogger(__name__)


class ProfilingSession(object):

    def __init__(self, stats, environ={}, timestamp=None):
        self._graph = None
        self._stats = stats
        self._uuid = uuid.uuid1()

        # Save some environment variables (if available)
        self.path = environ.get('PATH_INFO')

        # Some profiling session attributes need to be calculated
        self.duration = max([stat.totaltime for stat in stats])
        self.cutoff_percentage = 0.1
        self.cutoff_time = self.duration * self.cutoff_percentage
        self.timestamp = timestamp

        self._create_graph()

    def _create_graph(self):
        def generate_key(stat):
            # If we have a module, generate the module name (a.b.c, etc..)
            module = getmodule(stat.code)
            if module:
                return ".".join((module.__name__, stat.code.co_name))

            # Otherwise, return a path based on the filename and function name.
            return "%s.%s" % (stat.code.co_filename, stat.code.co_name)

        def valid_module(code):
            if isinstance(code, str):
                return False
            if code.co_filename.startswith("<"):
                return False
            return True

        # Create a graph; dot graphs need names, so just use `G' so that
        # pygraphviz doesn't complain when we render it.
        g = nx.DiGraph(name="G")
        stats = self._stats

        # Iterate through stats to add the original nodes
        for stat in stats:
            # Skip invalid modules
            if not valid_module(stat.code):
                continue

            caller_key = generate_key(stat)

            # Add all the calls as edges
            for call in stat.calls or []:
                # Skip invalid calls
                if not valid_module(call.code):
                    continue

                callee_key = generate_key(call)

                # If defined, cutoff subgraphs based on totaltime taken
                if self.cutoff_time and call.totaltime < self.cutoff_time:
                    log.debug(
                        "Skipping edge `%s' -> `%s', due to cutoff.",
                        caller_key, callee_key, call.totaltime)
                    continue

                attrs = {
                    'callcount': call.callcount,
                    'inlinetime': call.inlinetime,
                    'reccallcount': call.reccallcount,
                    'totaltime': call.totaltime,
                }

                # Add the edge using a weight and label
                g.add_edge(caller_key, callee_key,
                           weight=call.totaltime,
                           label=call.totaltime,
                           attr_dict=attrs)

        self._graph = g

    def draw_graph(self):
        filename = self.uuid + ".png"
        path = os.path.join(gettempdir(), filename)
        nx.to_agraph(self._graph).draw(path, prog="dot")
        log.info("Wrote output to `%s'" % path)

    @property
    def root_nodes(self):
        return [node
                for node, degree in self._graph.in_degree_iter()
                if degree == 0]

    @property
    def uuid(self):
        return str(self._uuid)
