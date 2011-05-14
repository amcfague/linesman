import os

from linesman.backends.pickle import PickleBackend
from linesman.tests import get_temporary_filename
from linesman.tests.backends import TestBackend


class TestBackendPickle(TestBackend):

    def setUp(self):
        self.filename = get_temporary_filename()
        self.backend = PickleBackend(self.filename)
        self.backend.setup()

    def tearDown(self):
        os.remove(self.db_filename)
