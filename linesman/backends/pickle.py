import logging

from linesman.backends import Backend


try:
    # Python 2.7+
    from collections import OrderedDict
except ImportError:
    # Python 2.4+
    from ordereddict import OrderedDict


try:
    import cPickle as pickle
except ImportError:
    import pickle


log = logging.getLogger(__name__)


class PickleBackend(Backend):
    """
    Stores entire session as a pickled object.  This can be extremely slow when
    using even smaller sets of sessions--on the order of 30mb, or around 200
    requests.
    """

    def __init__(self, filename="sessions.dat"):
        self.filename = filename

    def __flush(self):
        """
        Writes the session history to disk, in pickled form.
        """
        with open(self.filename, "w+b") as pickle_fd:
            pickle.dump(self._session_history,
                        pickle_fd,
                        pickle.HIGHEST_PROTOCOL)

    def setup(self, filename="sessions.dat"):
        """
        Reads in pickled data from ``filename``.
        """
        try:
            with open(self.filename, "rb") as pickle_fd:
                self._session_history = pickle.load(pickle_fd)
        except IOError:
            log.debug(
                "`%s' does not exist; creating new dictionary.",
                self.filename)
            self._session_history = OrderedDict()
        except ValueError:
            log.error("Could not unpickle `%s`; this is likely not "
                      "recoverable.  Please delete this file and start "
                      "from scratch.", self.filename)
            raise

    def add(self, session):
        """
        Adds a session to this dictionary and flushes it to disk.
        """
        self._session_history[session.uuid] = session
        self.__flush()

    def clear(self):
        """
        Clears the dictionary and flushes it to disk.
        """
        self._session_history.clear()
        self.__flush()

    def get(self, session_uuid):
        return self._session_history.get(session_uuid)

    def get_all(self):
        return self._session_history.copy()
