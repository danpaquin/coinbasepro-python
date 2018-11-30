class CbproException(Exception):
    """
    Base Coinbase Pro Exception
    Raised when Bad Response returned from Coinbase Pro
    See: https://docs.pro.coinbase.com/?r=1#errors
    """

    def __init__(self, message, code):
        """
        :param message: Message from Coinbase Pro response
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
    def code(self, code):
        self._code = code


class InvalidCbproRequest(CbproException):
    """
    Raised on 400 response from Coinbase Pro
    """
    pass


class UnauthorizedCbproRequest(CbproException):
    """
    Raised on 401 response from Coinbase Pro
    """
    pass


class ForbiddenCbproRequest(CbproException):
    """
    Raised on 403 response from Coinbase Pro
    """
    pass


class NotFoundCbproRequest(CbproException):
    """
    Raised on 404 response from Coinbase Pro
    """
    pass


class CbproRateLimitRequest(CbproException):
    """
    Raised on 429 response from Coinbase Pro
    """
    pass


class UnknownCbproClientRequest(CbproException):
    """
    Raised on 4XX responses not tracked
    """
    pass


class InternalErrorCbproRequest(CbproException):
    """
    Raised on 500 response from Coinbase Pro
    """
    pass
