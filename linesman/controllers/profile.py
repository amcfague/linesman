import logging

from linesman import backend, profiling_status, request, response
from linesman.controllers import BaseController
from linesman.templating import render


log = logging.getLogger(__name__)


class ProfileController(BaseController):

    def index(self):
        if 'enable' in request.params:
            profiling_status.enable()
        elif 'disable' in request.params:
            profiling_status.disable()

        session_history = backend.get_all()
        return render('list.tmpl', history=session_history, path=request.path,
                      profiling_enabled=profiling_status.is_enabled())

