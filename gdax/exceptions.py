class GdaxException(Exception):
    """
    Base GDAX Exception
    Raised when Bad Response returned from GDAX
    See: https://docs.gdax.com/?python#errors
    """

    def __init__(self, message, code):
        """
        :param message: Message from GDAX response
        :type message: str
        :param code: HTTP Code
        :type code: int
        """
        self._message = message
        self._code = code

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

    @property
    def code(self):
        return self._code

    @message.setter
    def message(self, code):
        self._code = code


class InvalidGdaxRequest(GdaxException):
    """
    Raised on 400 response from GDAX
    """
    pass


class UnauthorizedGdaxRequest(GdaxException):
    """
    Raised on 401 response from GDAX
    """
    pass


class ForbiddenGdaxRequest(GdaxException):
    """
    Raised on 403 response from GDAX
    """
    pass


class NotFoundGdaxRequest(GdaxException):
    """
    Raised on 404 response from GDAX
    """
    pass


class UnknownGdaxClientRequest(GdaxException):
    """
    Raised on 4XX responses not tracked
    """
    pass


class InternalErrorGdaxRequest(GdaxException):
    """
    Raised on 500 response from GDAX
    """
    pass
