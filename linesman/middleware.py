import logging
import sys
from cProfile import Profile

from mako.lookup import TemplateLookup
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from pkg_resources import resource_filename
from routes.util import URLGenerator
from webob import Request, Response
from webob.exc import HTTPException, HTTPNotFound

import linesman.routing
import linesman.status
from linesman.session import Session


log = logging.getLogger(__name__)


def profiler_filter_factory(conf, **kwargs):
    """
    Factory for creating :mod:`paste` filters. Full documentation can be found
    in `the paste docs <http://pythonpaste.org/deploy/#paste-filter-factory>`_.
    """
    def filter(app):
        return RegistryManager(ProfilingMiddleware(app, **kwargs))
    return filter


def profiler_filter_app_factory(app, conf, **kwargs):
    """
    Creates a single :mod:`paste` filter. Full documentation can be found in
    `the paste docs <http://pythonpaste.org/deploy/#paste-filter-factory>`_.
    """
    return RegistryManager(ProfilingMiddleware(app, **kwargs))


def make_linesman_middleware(app, **kwargs):
    """
    Helper function for wrapping an application with :mod:`!linesman`. This can
    be used when manually wrapping middleware.
    """
    return RegistryManager(ProfilingMiddleware(app, **kwargs))


class ProfilingMiddleware(object):

    STATIC_DIR = resource_filename("linesman", "static")
    TEMPLATES_DIR = resource_filename("linesman", "templates")

    def __init__(self, app,
                 profiler_path="__profiler__",
                 backend_str="linesman.backends.sqlite:SqliteBackend",
                 **kwargs):
        self.app = app
        self.prefix = profiler_path
        self.map = linesman.routing.make_map()
        self.__controller_cache = {}
        self._load_backend(backend_str, **kwargs)

    def __call__(self, environ, start_response):
        request = Request(environ)

        self._register_globals(environ, request)
        if request.path_info_peek() != self.prefix:
            return self.profile_app(environ, start_response)
        else:
            request.path_info_pop()

        # Return the specialized static parser for static data (images,
        # javascript, and CSS files.)
        if request.path_info_peek() == "static":
            request.path_info_pop()
            static_app = StaticURLParser(self.STATIC_DIR)
            return static_app(environ, start_response)

        # Set the request as a global object
        self._register_globals(environ, request)

        route_match = self.map.match(request.path_info) or {}
        if not route_match:
            return HTTPNotFound()(environ, start_response)

        try:
            self.dispatch(**route_match)
            return linesman.response(environ, start_response)
        except HTTPException as exc:
            return exc(environ, start_response)

    def _load_backend(self, backend_conf, **kwargs):
        module_name, _, class_name = backend_conf.rpartition(":")
        module = __import__(module_name, fromlist=[class_name], level=0)
        self._backend = getattr(module, class_name)(**kwargs)
        self._backend.setup()

    def _register_globals(self, environ, request):
        registry = environ['paste.registry']
        registry.register(linesman.backend, self._backend)
        registry.register(
            linesman.profiling_status, linesman.status.ProfilingStatus())
        registry.register(linesman.request, request)
        registry.register(linesman.response, Response(charset="utf-8"))
        registry.register(linesman.template_lookup, TemplateLookup(
            directories=[self.TEMPLATES_DIR]))
        registry.register(linesman.url, URLGenerator(self.map, environ))

    def get_action(self, controller_obj, action_name):
        try:
            return getattr(controller_obj, action_name)
        except:
            return None

    def get_controller(self, controller_name):
        controller_obj = self.__controller_cache.get(controller_name)
        if not controller_obj:
            controller_obj = self.load_controller(controller_name)

        return controller_obj

    def load_controller(self, controller_name):
        module_name = "linesman.controllers.%s" % controller_name
        class_name = controller_name.title() + "Controller"

        __import__(module_name)

        try:
            controller_obj = getattr(sys.modules[module_name], class_name)()
            self.__controller_cache[controller_name] = controller_obj
            return controller_obj
        except:
            return None

    def dispatch(self, controller, action, **kwargs):
        controller_obj = self.get_controller(controller)
        if not controller_obj:
            log.error("Controller `%s` not found.", controller)
            raise HTTPNotFound()

        action_func = self.get_action(controller_obj, action)
        if not action_func:
            log.error("Action name `%s` not found.", action)
            raise HTTPNotFound()

        body = action_func(**kwargs) or ""
        linesman.response.unicode_body = unicode(body)

    def profile_app(self, environ, start_response):
        if linesman.profiling_status.is_disabled():
            return self.app(environ, start_response)

        locals_ = locals()
        prof = Profile()
        prof.runctx(
            "app = self.app(environ, start_response)", globals(), locals_)

        # Convert the profile results to an object we can store reliably
        session = Session(path=environ.get("PATH_INFO", ""))
        session.load_stats(prof.getstats())
        self._backend.add(session)

        return locals_['app']
