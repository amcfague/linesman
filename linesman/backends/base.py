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


class Backend(object):
    """
    Base class for all backends.  Methods that raise a NotImplementedError
    exception are required to be overriden by children, while functions that
    pass are optional.
    """

    def __init__(self, *args, **kwargs):
        pass

    def setup(self):
        """
        Responsible for initializing the backend. for usage.  This is run once
        on middleware startup.

        Raises a :class:`NotImplementedError` exception.
        """
        raise NotImplementedError()

    def add(self, session):
        """
        Store a new session in history.

        Raises a :class:`NotImplementedError` exception.
        """
        raise NotImplementedError()

    def delete(self, session_uuid):
        """
        Removes a specific stored session from the history.

        This should return the number of rows removed (0 or 1).

        Raises a :class:`NotImplementedError` exception.
        """
        raise NotImplementedError()

    def delete_all(self):
        """
        Removes all stored sessions from the history.

        This should return the number of rows removed.

        Raises a :class:`NotImplementedError` exception.
        """
        raise NotImplementedError()

    def get(self, session_uuid):
        """
        Returns the data associated with ``session_uuid``.  Should return
        `None` if no session can be found with the specified uuid.

        Raises a :class:`NotImplementedError` exception.
        """
        raise NotImplementedError()

    def get_all(self):
        """
        Return a dictionary-like object of ALL sessions, where the key is the
        `session uuid`.

        Raises a :class:`NotImplementedError` exception.
        """
        raise NotImplementedError()
