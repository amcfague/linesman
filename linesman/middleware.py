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
import os
from cProfile import Profile
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


log = logging.getLogger(__name__)

# Graphs
GRAPH_DIR = os.path.join(gettempdir(), "linesman-graph")
MEDIA_DIR = resource_filename("linesman", "media")
TEMPLATES_DIR = resource_filename("linesman", "templates")
ENABLED_FLAG_FILE = 'linesman-enabled'

CUTOFF_TIME_UNITS = 1e9  # Nanoseconds per second


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
    ``backend``:
        This should be a full module path, with the function or class name
        specified after the trailing `:`.  This function or class should return
        an implementation of :class:`~linesman.backend.Backend`.
    ``chart_packages``:
        Space separated list of packages to be charted in the pie graph.
    """

    def __init__(self, app,
                       profiler_path="/__profiler__",
                       backend="linesman.backends.sqlite:SqliteBackend",
                       chart_packages="",
                       **kwargs):
        self.app = app
        self.profiler_path = profiler_path

        # Always reverse sort these packages, so that child packages of the
        # same module will always be picked first.
        self.chart_packages = sorted(chart_packages.split(), reverse=True)

        # Setup the backend
        module_name, sep, class_name = backend.rpartition(":")
        module = __import__(module_name, fromlist=[class_name], level=0)
        self._backend = getattr(module, class_name)(**kwargs)

        # Attempt to create the GRAPH_DIR
        if not os.path.exists(GRAPH_DIR):
            try:
                os.makedirs(GRAPH_DIR)
            except IOError:
                log.error("Could not create directory `%s'", GRAPH_DIR)
                raise

        # Setup the Mako template lookup
        self.template_lookup = TemplateLookup(directories=[TEMPLATES_DIR])

        # Set it up
        self._backend.setup()

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

        self.profiling_enabled = os.path.exists(ENABLED_FLAG_FILE)
        if req.path_info_peek() != self.profiler_path.strip('/'):
            if not self.profiling_enabled:
                return self.app(environ, start_response)
            _locals = locals()
            prof = Profile()
            start_timestamp = datetime.now()
            prof.runctx(
                "app = self.app(environ, start_response)", globals(), _locals)
            stats = prof.getstats()
            session = ProfilingSession(stats, environ, start_timestamp)
            self._backend.add(session)

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
        elif query_param == "delete":
            wsgi_app = self.delete_profile(req)
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

    def list_profiles(self, req):
        """
        Displays all available profiles in list format.

        ``req``:
            :class:`webob.Request` containing the environment information from
            the request itself.

        Returns a WSGI application.
        """
        if 'enable' in req.params:
            try:
                if not os.path.exists(ENABLED_FLAG_FILE):
                    open(ENABLED_FLAG_FILE, 'w').close()
                self.profiling_enabled = True
            except IOError:
                log.error("Unable to create %s to enable profiling",
                          os.path.abspath(ENABLED_FLAG_FILE))
                raise
        elif 'disable' in req.params:
            try:
                if os.path.exists(ENABLED_FLAG_FILE):
                    os.remove(ENABLED_FLAG_FILE)
                self.profiling_enabled = False
            except IOError:
                log.error("Unable to delete %s to disable profiling",
                          os.path.abspath(ENABLED_FLAG_FILE))
                raise

        resp = Response(charset='utf8')
        session_history = self._backend.get_all()
        resp.unicode_body = self.get_template('list.tmpl').render_unicode(
            history=session_history,
            path=req.path,
            profiling_enabled=self.profiling_enabled)
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
        session = self._backend.get(session_uuid)
        if session:
            force_thumbnail_creation = False

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

    def delete_profile(self, req):
        """
        If the current path info refers to a specific ``session_uuid``, this
        session will be removed.  Otherwise, if it refers to `all`, then all
        tracked session info will be removed.

        ``req``:
            :class:`webob.Request` containing the environment information from
            the request itself.

        Returns a WSGI application.
        """
        resp = Response(charset='utf8')
        session_uuid = req.path_info_pop()
        if session_uuid == "all":
            deleted_rows = self._backend.delete_all()
        elif session_uuid:
            deleted_rows = self._backend.delete(session_uuid)
        else:
            deleted_rows = 0

        resp.text = "%d row(s) deleted." % deleted_rows

        return resp

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
        session = self._backend.get(session_uuid)

        # If the Session doesn't exist, return an appropriate error
        if not session:
            resp.status = "404 Not Found"
            resp.text = "Session `%s' not found." % session_uuid
        else:
            # Otherwise, prepare the graph for display!
            cutoff_percentage = float(
                req.params.get('cutoff_percent', 5) or 5) / 100
            cutoff_time = int(
                session.duration * cutoff_percentage * CUTOFF_TIME_UNITS)
            graph, root_nodes, removed_edges = prepare_graph(
                session._graph, cutoff_time, True)
            chart_values = time_per_field(session._graph, root_nodes,
                                        self.chart_packages)
            resp.text = self.get_template('tree.tmpl').render_unicode(
                session=session,
                graph=graph,
                root_nodes=root_nodes,
                removed_edges=removed_edges,
                application_url=self.profiler_path,
                cutoff_percentage=cutoff_percentage,
                cutoff_time=cutoff_time,
                chart_values=chart_values
            )

        return resp


def time_per_field(full_graph, root_nodes, fields):
    """
    This function generates the fields used by the pie graph jQuery code on the
    session profile page.  This process is clever about calculating total time,
    so that packages and subpackages don't overlap.

    Additionally, if I were to track ``linesman.middleware``, and in that
    package an external package is called, say ``re``, the time spent in ``re``
    would be added to the total time in package ``linesman.middleware``, unless
    ``re`` is one of the fields that are being tracked.

    ``full_graph``:
        For best results, this should be an untouched copy of the original
        graph.  The reasoning is because, if certain packages are pruned, the
        graph result could be completely varied and inaccurate.
    ``root_nodes``:
        The list of starting point for this graph.
    ``fields``:
        The list of packages to be tracked.

    Returns a dictionary where the keys are the same as the ``fields``, plus an
    extra field called `Other` that contains packages that were not tracked.
    The values for each field is the total time spent in that package.

    .. warning::

        This will run into issues where separate packages rely on the same core
        set of functions.  I.e., of `PackageA` and `PackageB` both rely on
        ``re``, there's no defined outcome.  Whichever one is parsed first will
        include the time spent in ``re``.
    """
    if not fields:
        return

    # Keep track of all the nodes we've seen.
    seen_nodes = []
    values = dict((field, 0.0) for field in fields)
    values["Other"] = 0.0

    def is_field(node_name):
        """
        Returns True if ``node_name`` is part of the ``fields`` that should be
        tracked.
        """
        for field in fields:
            if node_name.startswith(field + "."):
                return field
        return None

    def recursive_parse(node_name, last_seen_field=None):
        """
        Given a node, follow its descendents and append their runtimes to the
        last seen "tracked" field.
        """
        if node_name in seen_nodes:
            return
        seen_nodes.append(node_name)

        field = is_field(node_name)
        inlinetime = full_graph.node[node_name]['inlinetime']
        if field:
            last_seen_field = field

        if last_seen_field:
            values[last_seen_field] += inlinetime
        else:
            values["Other"] += inlinetime

        # Parse the successors
        for node in full_graph.successors(node_name):
            recursive_parse(node, last_seen_field)

    for root_node in root_nodes:
        recursive_parse(root_node)

    return values


def prepare_graph(source_graph, cutoff_time, break_cycles=False):
    """
    Prepares a graph for display.  This includes:

        - removing subgraphs based on a cutoff time
        - breaking cycles

    Returns a tuple of (new_graph, removed_edges)
    """
    # Always use a copy for destructive changes
    graph = source_graph.copy()

    # Some node data could be empty dict
    for node, data in graph.nodes(data=True):
        if not data:
            data['totaltime'] = 0

    max_totaltime = max(data['totaltime']
                        for node, data in graph.nodes(data=True))
    for node, data in graph.nodes(data=True):
        data['color'] = "%f 1.0 1.0" % (
            (1 - (data['totaltime'] / max_totaltime)) / 3)
        data['style'] = 'filled'

    cyclic_breaks = []

    # Remove nodes where the totaltime is greater than the cutoff time
    graph.remove_nodes_from([
        node
        for node, data in graph.nodes(data=True)
        if int(data.get('totaltime') * CUTOFF_TIME_UNITS) < cutoff_time])

    # Break cycles
    if break_cycles:
        for cycle in nx.simple_cycles(graph):
            u, v = cycle[0], cycle[1]
            if graph.has_edge(u, v):
                graph.remove_edge(u, v)
                cyclic_breaks.append((u, v))

    root_nodes = [node
                  for node, degree in graph.in_degree_iter()
                  if degree == 0]

    return graph, root_nodes, cyclic_breaks


def profiler_filter_factory(conf, **kwargs):
    """
    Factory for creating :mod:`paste` filters.  Full documentation can be found
    in `the paste docs <http://pythonpaste.org/deploy/#paste-filter-factory>`_.
    """
    def filter(app):
        return ProfilingMiddleware(app, **kwargs)
    return filter


def profiler_filter_app_factory(app, conf, **kwargs):
    """
    Creates a single :mod:`paste` filter.  Full documentation can be found in
    `the paste docs <http://pythonpaste.org/deploy/#paste-filter-factory>`_.
    """
    return ProfilingMiddleware(app, **kwargs)


def make_linesman_middleware(app, **kwargs):
    """
    Helper function for wrapping an application with :mod:`!linesman`.  This
    can be used when manually wrapping middleware, although its also possible
    to simply call :class:`~linesman.middleware.ProfilingMiddleware` directly.
    """
    return ProfilingMiddleware(app, **kwargs)
