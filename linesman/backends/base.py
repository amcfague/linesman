class Backend(object):
    """
    Base class for all backends.  Methods that raise a NotImplemented exception
    are required to be overriden by children, while functions that pass are
    optional.
    """

    def __init__(self, *args, **kwargs):
        pass

    def setup(self):
        """
        Responsible for initializing the backend. for usage.  This is run once
        on middleware startup.

        Raises a :class:`NotImplemented` exception.
        """
        raise NotImplemented()

    def add(self, session):
        """
        Store a new session in history.

        Raises a :class:`NotImplemented` exception.
        """
        raise NotImplemented()

    def clear(self):
        """
        Removes all stored sessions from the history.

        Raises a :class:`NotImplemented` exception.
        """
        raise NotImplemented()

    def get(self, session_uuid):
        """
        Returns the data associated with ``session_uuid``.  Should return
        `None` if no session can be found with the specified uuid.

        Raises a :class:`NotImplemented` exception.
        """
        raise NotImplemented()

    def get_all(self):
        """
        Return a dictionary-like object of ALL sessions, where the key is the
        `session uuid`.

        Raises a :class:`NotImplemented` exception.
        """
        raise NotImplemented()
