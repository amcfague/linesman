import logging
import sys

from webob import Request
from webob.exc import HTTPNotFound

from linesman.routing import make_map


log = logging.getLogger(__name__)


def profiler_filter_factory(conf, **kwargs):
    """
    Factory for creating :mod:`paste` filters. Full documentation can be found
    in `the paste docs <http://pythonpaste.org/deploy/#paste-filter-factory>`_.
    """
    def filter(app):
        return ProfilingMiddleware(app, **kwargs)
    return filter


def profiler_filter_app_factory(app, conf, **kwargs):
    """
    Creates a single :mod:`paste` filter. Full documentation can be found in
    `the paste docs <http://pythonpaste.org/deploy/#paste-filter-factory>`_.
    """
    return ProfilingMiddleware(app, **kwargs)


def make_linesman_middleware(app, **kwargs):
    """
    Helper function for wrapping an application with :mod:`!linesman`. This can
    be used when manually wrapping middleware, although its also possible to
    simply call :class:`~linesman.middleware.ProfilingMiddleware` directly.
    """
    return ProfilingMiddleware(app, **kwargs)


class ProfilingMiddleware(object):

    def __init__(self, app, profiler_path="__profiler__", **kwargs):
        self.app = app
        self.prefix = profiler_path
        self.map = make_map()

    def __call__(self, environ, start_response):
        request = Request(environ)

        if request.path_info_peek() != self.prefix:
            return self.app(environ, start_response)

        request.path_info_pop()
        return self.dispatch(request)(environ, start_response)

    def dispatch(self, request):
        route_match = self.map.match(request.path_info)

        controller_name = route_match["controller"]
        action_name = route_match["action"]

        module_name = "linesman.controllers.%s" % controller_name
        class_name =  "%sController" % controller_name.title()

        __import__(module_name)
        try:
            controller_obj = getattr(sys.modules[module_name], class_name)
        except AttributeError:
            log.error("No class `%s`.", class_name)
            return HTTPNotFound()
        except KeyError:
            log.error("No module `%s`.", module_name)
            raise
            return HTTPNotFound()

        try:
            action_func = getattr(controller_obj, action_name)
        except AttributeError:
            log.error("No function `%s.%s`.", class_name, action_name)
            return HTTPNotFound()

        return action_func(request)
