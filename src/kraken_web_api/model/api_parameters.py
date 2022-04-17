from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class ApiParameters:
    """ Parameters of API """
    api_key: str
    api_secret: str
