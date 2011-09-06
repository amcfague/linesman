from linesman.controllers import BaseController
from linesman import backend


class ProfileController(BaseController):

    def index(self):
        return "It vorks!"

    def delete(self, id):
        pass

    def view(self, id):
        pass
