from nose.tools import raises

from linesman.backends.base import Backend
from linesman.tests.backends import TestBackend


class TestBaseBackend(TestBackend):

    def setUp(self):
        self.backend = Backend()

    @raises(NotImplementedError)
    def test_setup_not_implemented(self):
        """ Test that setup raises NotImplementedError. """
        self.backend.setup()

    @raises(NotImplementedError)
    def test_add_not_implemented(self):
        """ Test thatdd raises NotImplementedError. """
        self.backend.add(None)

    @raises(NotImplementedError)
    def test_delete_not_implemented(self):
        """ Test that delete raises NotImplementedError. """
        self.backend.delete(None)

    @raises(NotImplementedError)
    def test_delete_many_not_implemented(self):
        """ Test that delete_many raises NotImplementedError. """
        self.backend.delete_many([None])

    @raises(NotImplementedError)
    def test_delete_all_not_implemented(self):
        """ Test that delete_all raises NotImplementedError. """
        self.backend.delete_all()

    @raises(NotImplementedError)
    def test_get_not_implemented(self):
        """ Test that get raises NotImplementedError. """
        self.backend.get(None)

    @raises(NotImplementedError)
    def test_get_all_not_implemented(self):
        """ Test that get_all raises NotImplementedError. """
        self.backend.get_all()
