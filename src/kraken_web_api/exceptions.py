class SocketConnectionError(Exception):
    """ Could not connect to kraken websocket """
    pass


class InvalidJsonException(Exception):
    """ Incorrect JSON data from Kraken """
    pass


class BookDataHandlingException(Exception):
    """ Can't handle book data recieved """
    pass
