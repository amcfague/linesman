import os
import tempfile


class ProfilingStatus(object):

    def __init__(self):
        self.status_path = os.path.join(
            tempfile.gettempdir(), ".linesman-enabled")

    def is_enabled(self):
        return os.path.exists(self.status_path)

    def is_disabled(self):
        return not self.is_enabled()

    def enable(self):
        if self.is_disabled():
            os.mkdir(self.status_path)

    def disable(self):
        if self.is_enabled():
            os.rmdir(self.status_path)

    def toggle(self):
        if self.is_enabled():
            self.disable()
        else:
            self.enable()
