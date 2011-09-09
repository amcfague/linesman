import inspect
import uuid
from datetime import datetime


def generate_key(code):
    # First, check if its built-in (i.e., code is a string)
    if isinstance(code, str):
        return code

    # If we have a module, generate the module name (a.b.c, etc..)
    module = inspect.getmodule(code)
    if module:
        return ".".join((module.__name__, code.co_name))

    # Otherwise, return a path based on the filename and function name.
    return "%s.%s" % (code.co_filename, code.co_name)


class Session(object):

    def __init__(self, duration=0.0, path=""):
        self.path = path
        self.timestamp = datetime.now()
        self.duration = duration
        self.uuid = str(uuid.uuid1())

        self.nodes = {}
        self.edges = {}
        self.edge_attrs = {}
    
    def load_stats(self, stats):
        for stat in stats:
            caller_key = generate_key(stat.code)
            attrs = {
                'callcount': stat.callcount,
                'inlinetime': stat.inlinetime,
                'reccallcount': stat.reccallcount,
                'totaltime': stat.totaltime}

            self.add_node(caller_key, attrs)
            self.duration = max((self.duration, stat.totaltime))

            for call in stat.calls or []:
                callee_key = generate_key(call.code)
                call_attrs = {
                    'callcount': call.callcount,
                    'inlinetime': call.inlinetime,
                    'reccallcount': call.reccallcount,
                    'totaltime': call.totaltime}

                self.add_edge(caller_key, callee_key, call_attrs)

    def add_node(self, name, attrs):
        self.nodes[name] = attrs

    def add_edge(self, name1, name2, attrs):
        if name1 not in self.edges:
            self.edges[name1] = []

        self.edges[name1].append(name2)
        self.edge_attrs[(name1, name2)] = attrs
