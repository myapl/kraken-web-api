
import time
from kraken_web_api.model.api_parameters import ApiParameters


class ApiClient:
    def __init__(self, parameters: ApiParameters) -> None:
        self.parameters = parameters

    def _nonce(self):
        """ Nonce counter.
        :returns: an always-increasing unsigned integer (up to 64 bits wide)
        """
        return int(1000*time.time())
