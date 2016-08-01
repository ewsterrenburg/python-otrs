"""OTRS :: session :: operations."""
from otrs.client import OperationBase


class Session(OperationBase):
    """Base class for OTRS Session:: operations."""


class SessionCreate(Session):
    """Class to handle OTRS Session::SessionCreate operation."""

    def __call__(self, password, user_login=None, customer_user_login=None):
        """Create an User session or CustomerUser session.

        @returns the session_id
        """
        if user_login:
            ret = self.req('SessionCreate',
                           UserLogin=user_login,
                           Password=password)
        else:
            ret = self.req('SessionCreate',
                           CustomerUserLogin=customer_user_login,
                           Password=password)
        signal = self._unpack_resp_one(ret)
        session_id = signal.text

        # sets the session id for the entire client to this
        self.session_id = session_id

        # returns the session id in case you want it,
        # but its not normally needed
        return session_id
