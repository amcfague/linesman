import cPickle
import logging
import os
from datetime import datetime
from tempfile import gettempdir

import Image
import networkx as nx
from mako.lookup import TemplateLookup
from paste.urlparser import StaticURLParser
from pkg_resources import resource_filename
from webob import Request, Response
from webob.exc import HTTPNotFound

from linesman import ProfilingSession, draw_graph


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


log = logging.getLogger(__name__)

# Graphs
GRAPH_DIR = os.path.join(gettempdir(), "linesman-graph")
MEDIA_DIR = resource_filename("linesman", "media")
TEMPLATES_DIR = resource_filename("linesman", "templates")

CUTOFF_TIME_UNITS = 1e9 # Nanoseconds per second

class ProfilingMiddleware(object):
    """
    This wraps calls to the WSGI application with cProfile, storing the
    output and providing useful graphs for the user to view.

    ``app``:
        WSGI application
    ``profiler_path``:
        Path relative to the root to look up.  For example, if your script is
        mounted at the context `/someapp` and this variable is set to
        `/__profiler__`, `/someapp/__profiler__` will match.
    ``session_history_path``:
        When storing persistant data, store the pickled data objects in this
        file.
    """

    def __init__(self, app,
                       profiler_path="/__profiler__",
                       session_history_path="sessions.dat",
                       **kwargs):
        self.app = app
        self.profiler_path = profiler_path
        self.session_history_path = session_history_path

        # Attempt to create the GRAPH_DIR
        if not os.path.exists(GRAPH_DIR):
            try:
                os.makedirs(GRAPH_DIR)
            except IOError:
                log.error("Could not create directory `%s'", GRAPH_DIR)
                raise

        # Setup the Mako template lookup
        self.template_lookup = TemplateLookup(directories=[TEMPLATES_DIR])

        # Try to read stored sessions on disk
        try:
            with open(self.session_history_path, "rb") as pickle_fd:
                self._session_history = cPickle.load(pickle_fd)
        except IOError:
            log.debug("`%s' does not exist; creating new dictionary.",
                                                self.session_history_path)
            self._session_history = OrderedDict()
        except ValueError as exc:
            raise ValueError("Could not unpickle data; please remove `%s`." % \
                      self.session_history_path) 

    def __call__(self, environ, start_response):
        """
        This will be called when the application is being run.  This can be
        either:

            - a request to the __profiler__ framework to display profiled
              information, or
            - a normal request that will be profiled.

        Returns the WSGI application.
        """
        # If we're not accessing the profiler, profile the request.
        req = Request(environ)
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

        # We could import `routes` and use something like that here, but since
        # not all frameworks use this, it might become an external dependency
        # that isn't needed.  So parse the URL manually using :class:`webob`.
        query_param = req.path_info_pop()
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

    def get_template(self, template):
        """
        Uses mako templating lookups to retrieve the template file.  If the
        file is ever changed underneath, this function will automatically
        retrieve and recompile the new version.

        ``template``:
            Filename of the template, relative to the `linesman/templates`
            directory.
        """
        return self.template_lookup.get_template(template)

    def __flush_sessions(self):
        """ Flushes all session data to disk. """
        with open(self.session_history_path, "w+b") as pickle_fd:
            cPickle.dump(self._session_history, pickle_fd, cPickle.HIGHEST_PROTOCOL)

    def _add_session(self, session):
        """ Adds session data to the profiler's history. """
        self._session_history[session.uuid] = session
        self.__flush_sessions()

    def _clear_sessions(self):
        """ Removes all session data from history. """
        self._session_history.clear()
        self.__flush_sessions()

    def list_profiles(self, req):
        """
        Displays all available profiles in list format.

        ``req``:
            :class:`webob.Request` containing the environment information from
            the request itself.

        Returns a WSGI application.
        """
        resp = Response(charset='utf8')
        resp.unicode_body = self.get_template('list.tmpl').render_unicode(
            history=self._session_history,
            application_url=req.application_url)
        return resp

    def media(self, req):
        """
        Serves up static files relative to ``MEDIA_DIR``.

        ``req``:
            :class:`webob.Request` containing the environment information from
            the request itself.

        Returns a WSGI application.
        """
        return StaticURLParser(MEDIA_DIR)

    def render_graph(self, req):
        """
        Used to display rendered graphs; if the graph that the user is trying
        to access does not exist--and the ``session_uuid`` exists in our
        history--it will be rendered.

        This also creates a thumbnail image, since some of these graphs can
        grow to be extremely large.

        ``req``:
            :class:`webob.Request` containing the environment information from
            the request itself.

        Returns a WSGI application.
        """
        path_info = req.path_info_peek()
        if '.' not in path_info:
            return StaticURLParser(GRAPH_DIR)
        
        fileid, _, ext = path_info.rpartition('.')
        if path_info.startswith("thumb-"):
            fileid = fileid[6:]

        if '--' not in fileid:
            return StaticURLParser(GRAPH_DIR)

        session_uuid, _, cutoff_time = fileid.rpartition('--')
        cutoff_time = int(cutoff_time)

        # We now have the session_uuid
        if session_uuid in self._session_history:
            force_thumbnail_creation = False
            session = self._session_history[session_uuid]

            filename = "%s.png" % fileid
            path = os.path.join(GRAPH_DIR, filename)
            if not os.path.exists(path):
                graph, root_nodes, removed_edges = prepare_graph(
                    session._graph, cutoff_time, False)
                draw_graph(graph, path)
                force_thumbnail_creation = True

            thumbnail_filename = "thumb-%s.png" % fileid
            thumbnail_path = os.path.join(GRAPH_DIR, thumbnail_filename)
            if not os.path.exists(thumbnail_path) or force_thumbnail_creation:
                log.debug("Creating thumbnail for %s at %s.", session_uuid,
                                                              thumbnail_path)
                im = Image.open(path, 'r')
                im.thumbnail((600, 600), Image.ANTIALIAS)
                im.save(thumbnail_path)

        return StaticURLParser(GRAPH_DIR)

    def show_profile(self, req):
        """
        Displays specific profile information for the ``session_uuid``
        specified in the path.

        ``req``:
            :class:`webob.Request` containing the environment information from
            the request itself.

        Returns a WSGI application.
        """
        resp = Response(charset='utf8')
        session_uuid = req.path_info_pop()
        if session_uuid not in self._session_history:
            resp.status = "404 Not Found"
            resp.body = "Session `%s' not found." % session_uuid
        else:
            cutoff_percentage = float(req.str_params.get('cutoff_percent', 5) or 5)/100
            session = self._session_history[session_uuid]
            cutoff_time = int(session.duration * cutoff_percentage * CUTOFF_TIME_UNITS)
            graph, root_nodes, removed_edges = prepare_graph(
                session._graph, cutoff_time, True)
            resp.unicode_body = self.get_template('tree.tmpl').render_unicode(
                session=session,
                graph=graph,
                root_nodes=root_nodes,
                removed_edges=removed_edges,
                application_url=self.profiler_path,
                cutoff_percentage = cutoff_percentage,
                cutoff_time = cutoff_time
            )

        return resp


def prepare_graph(source_graph, cutoff_time, break_cycles=False):
    """
    Prepares a graph for display.  This includes:

        - removing subgraphs based on a cutoff time
        - breaking cycles

    Returns a tuple of (new_graph, removed_edges)
    """
    # Always use a copy for destructive changes
    graph = source_graph.copy()

    max_totaltime = max(data['totaltime'] for node, data in graph.nodes(data = True))
    for node, data in graph.nodes(data=True):
        data['color'] = "%f 1.0 1.0" % ((1-(data['totaltime'] / max_totaltime)) / 3)
        data['style'] = 'filled'

    cyclic_breaks = []

    # Remove nodes where the totaltime is greater than the cutoff time
    graph.remove_nodes_from([node for node, data in graph.nodes(data=True)
                              if int(data.get('totaltime')*CUTOFF_TIME_UNITS) < cutoff_time])

    # Break cycles
    if break_cycles:
        for cycle in nx.simple_cycles(graph):
            u, v = cycle[0], cycle[1]
            if graph.has_edge(u, v):
                graph.remove_edge(u, v)
                cyclic_breaks.append((u, v))

    root_nodes = [node for node, degree in graph.in_degree_iter() if degree == 0]

    return graph, root_nodes, cyclic_breaks


def profiler_filter_factory(conf, **kwargs):
    def filter(app):
        return ProfilingMiddleware(app, **kwargs)
    return filter


def profiler_filter_app_factory(app, conf, **kwargs):
    return ProfilingMiddleware(app, **kwargs)
