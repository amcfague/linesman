from linesman.controllers import BaseController
from paste.urlparser import StaticURLParser
from pkg_resources import resource_filename


class MediaController(BaseController):

    MEDIA_DIR = resource_filename("linesman", "media")

    def static(self, request):
        return StaticURLParser(self.MEDIA_DIR)
