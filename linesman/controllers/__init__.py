from webob.exc import HTTPNotFound


class BaseController(object):

    def __dispatch(self, request):
        action = request.path_info_pop()
        try:
            return getattr(self, action)(request)
        except AttributeError:
            return HTTPNotFound()
