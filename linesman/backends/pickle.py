# This file is part of linesman.
#
# linesman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# linesman is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with linesman.  If not, see <http://www.gnu.org/licenses/>.
#
import cPickle
import logging

from linesman.backends.base import Backend


try:
    # Python 2.7+
    from collections import OrderedDict
except ImportError: #pragma no cover
    # Python 2.4+
    from ordereddict import OrderedDict


log = logging.getLogger(__name__)


class PickleBackend(Backend):
    """
    Stores entire session as a pickled object.  This can be extremely slow when
    using even smaller sets of sessions--on the order of 30mb, or around 200
    requests.
    """

    def __init__(self, filename="sessions.dat"):
        self.filename = filename

    def _flush(self):
        """
        Writes the session history to disk, in pickled form.
        """
        with open(self.filename, "w+b") as pickle_fd:
            cPickle.dump(self._session_history,
                        pickle_fd,
                        cPickle.HIGHEST_PROTOCOL)

    def setup(self):
        """
        Reads in pickled data from ``filename``.
        """
        try:
            with open(self.filename, "rb") as pickle_fd:
                self._session_history = cPickle.load(pickle_fd)
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
        self._flush()

    def delete(self, session_uuid):
        """
        Remove a session from the dictionary and flush it to disk.
        """
        if self.get(session_uuid):
            del self._session_history[session_uuid]
            self._flush()
            return 1

        return 0

    def delete_all(self):
        """
        Clear the entire session history and flush it to disk.
        """
        deleted_rows = len(self._session_history)
        self._session_history.clear()
        self._flush()

        return deleted_rows

    def get(self, session_uuid):
        return self._session_history.get(session_uuid)

    def get_all(self):
        return self._session_history.copy()
