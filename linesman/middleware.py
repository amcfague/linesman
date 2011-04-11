try:
    # Python 2.7+
    from collections import OrderedDict
except ImportError:
    # Python 2.4+ (need to easy_install)
    from ordereddict import OrderedDict

try:
    from cProfile import Profile
except ImportError:
    from profile import Profile

from datetime import datetime
from linesman import ProfilingSession, draw_graph
from mako.template import Template
from os import makedirs
from os.path import dirname, exists, join
from paste.urlparser import StaticURLParser
from pkg_resources import resource_filename
from tempfile import gettempdir
from webob import Request, Response
from webob.exc import HTTPNotFound

import cPickle
import logging
import mimetypes
import networkx as nx

log = logging.getLogger(__name__)

# Graphs
GRAPH_DIR = join(gettempdir(), "linesman-graph")
MEDIA_DIR = resource_filename("linesman", "media")
TEMPLATES_DIR = resource_filename("linesman", "templates")

# Templates
session_tree_template = Template(filename=join(TEMPLATES_DIR, "tree.tmpl"))
session_listing_template = Template(filename=join(TEMPLATES_DIR, "list.tmpl"))

try:
    makedirs(GRAPH_DIR)
except: pass

def prepare_graph(source_graph, cutoff_time, break_cycles=False):
    """
    Prepares a graph for display.  This includes:

        - removing subgraphs based on a cutoff time
        - breaking cycles

    Returns a tuple of (new_graph, removed_edges)
    """
    # Always use a copy for destructive changes
    g = source_graph.copy()
    cyclic_breaks = []

    # Remove nodes where the totaltime is greater than the cutoff time
    g.remove_nodes_from([node for node, data in g.nodes(data=True)
                              if data.get('totaltime') < cutoff_time])
   
    # Break cycles
    if break_cycles:
        for cycle in nx.simple_cycles(g):
            u, v = cycle[0], cycle[1]
            g.remove_edge(u, v)
            cyclic_breaks.append((u,v))

    root_nodes = [node for node, degree in g.in_degree_iter() if degree == 0]

    return g, root_nodes, cyclic_breaks


class ProfilingMiddleware(object):

    def __init__(self, app,
                       profiler_path="/__profiler__",
                       session_history_path="sessions.dat"):
        self.app = app
        self.profiler_path = profiler_path
        self.session_history_path = session_history_path

        # Try to read stored sessions on disk
        try:
            with open(self.session_history_path, "rb") as pickle_fd:
                self._session_history = cPickle.load(pickle_fd)
        except IOError:
            log.debug("`%s' does not exist; creating new dictionary.", self.session_history_path)
            self._session_history = OrderedDict()

    def __call__(self, environ, start_response):
        # If we're not accessing the profiler, profile the request.
        req = Request(environ)
        print req.path_info_peek()
        if req.path_info_peek() != self.profiler_path.strip('/'):
            _locals = locals()
            prof = Profile()
            start_timestamp = datetime.now()
            prof.runctx(
                "app = self.app(environ, start_response)", globals(), _locals)
            stats = prof.getstats()
            session = ProfilingSession(stats, environ, start_timestamp)
            self._add_session(session)

            return _locals['app']

        req.path_info_pop()
        query_param = req.path_info_pop()
        print dir(req)
        print req.application_url
        print req.path_url
        if not query_param:
            wsgi_app = self.list_profiles(req)
        elif query_param == "graph":
            wsgi_app = self.render_graph(req)
        elif query_param == "media":
            wsgi_app = self.media(req)
        elif query_param == "profiles":
            wsgi_app = self.show_profile(req)
        else:
            wsgi_app = HTTPNotFound()
        
        return wsgi_app(environ, start_response)

    def __flush_sessions(self):
        """ Flushes all sessions to disk. """
        with open(self.session_history_path, "w+b") as pickle_fd:
            cPickle.dump(self._session_history, pickle_fd)

    def _add_session(self, session):
        """ Adds a session to the profiler's history. """
        self._session_history[session.uuid] = session
        self.__flush_sessions()

    def _clear_sessions(self):
        """ Removes all sessions from history. """
        self._session_history.clear()
        self.__flush_sessions()

    def list_profiles(self, req):
        resp = Response()
        resp.body = session_listing_template.render(
            history=self._session_history,
            application_url=req.application_url)
        return resp

    def media(self, req):
        return StaticURLParser(MEDIA_DIR)

    def render_graph(self, req):
        print "rendering graph"
        session_uuid, ext = tuple(req.path_info_peek().rsplit(".", 1))
        filename = "%s.png" % session_uuid
        path = join(GRAPH_DIR, filename)
        if session_uuid in self._session_history and not exists(path):
            session = self._session_history[session_uuid]
            graph, root_nodes, removed_edges = prepare_graph(
                session._graph, session.cutoff_time, False)
            draw_graph(graph, path)
        return StaticURLParser(GRAPH_DIR)

    def show_profile(self, req):
        resp = Response()
        session_uuid = req.path_info_pop()
        if session_uuid not in self._session_history:
            resp.status = "404 Not Found"
            resp.body = "Session `%s' not found." % session
        else:
            session = self._session_history[session_uuid]
            graph, root_nodes, removed_edges = prepare_graph(
                session._graph, session.cutoff_time, True)
            resp.body = session_tree_template.render(
                session=session, graph=graph, root_nodes=root_nodes,
                removed_edges=removed_edges,
                application_url=self.profiler_path)

        return resp
