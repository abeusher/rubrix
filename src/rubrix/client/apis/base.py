from rubrix.client.sdk.client import AuthenticatedClient


class AbstractAPI:
    def __init__(self, client: AuthenticatedClient):
        self.__client__ = client
