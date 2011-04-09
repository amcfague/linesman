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

from os.path import dirname, join
from mako.template import Template
from linesman import ProfilingSession
from datetime import datetime


# Global Session object to keep track of ALL requests.
SESSION_HISTORY = OrderedDict()

TEMPLATES_DIR = join(dirname(__file__), "templates")
session_tree_template = Template(filename=join(TEMPLATES_DIR, "tree.tmpl"))
session_listing_template = Template(filename=join(TEMPLATES_DIR, "list.tmpl"))


class ProfilingMiddleware(object):

    def __init__(self, app, profiler_path="/__profiler__"):
        self.app = app
        self.profiler_path = profiler_path

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.profiler_path):
            return self.profiler_handler(environ, start_response)

        _locals = locals()
        _globals = globals()

        prof = Profile()
        start_timestamp = datetime.now()
        prof.runctx("app = self.app(environ, start_response)",
                                                    _globals, _locals)

        stats = prof.getstats()
        session = ProfilingSession(stats, environ, start_timestamp)
        SESSION_HISTORY[session.uuid] = session

        return _locals['app']

    def profiler_handler(self, environ, start_response):
        status = "200 OK"
        body = None
        headers = {'Content-Type': 'text/html'}

        PATH_INFO = environ['PATH_INFO']

        # Because the root WSGI application can be mounted on a context, use
        # the SCRIPT_NAME to get the full path relative to the document root.
        if 'SCRIPT_NAME' in environ:
            full_path = environ['SCRIPT_NAME'] + self.profiler_path
        else:
            full_path = self.profiler_path

        if PATH_INFO == self.profiler_path:
            # Display the list
            body = session_listing_template.render(
                history=SESSION_HISTORY, full_path=full_path)
        else:
            # Display the specific profile
            session = PATH_INFO.rsplit('/', 1)[1]
            if session not in SESSION_HISTORY:
                status = "404 Not found"
                body = "Session `%s' could not be found." % session
            else:
                body = session_tree_template.render(
                                    session=SESSION_HISTORY[session])

        # Calculate the Content-Length
        headers['Content-Length'] = len(body)

        # start_response *must* be called before returning content!
        start_response(status, headers.items())

        # The return must be a iterator of sorts--so use a list.
        return [body]
