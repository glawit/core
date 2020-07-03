import logging

logger = logging.getLogger(
    __name__,
)


class Session:
    def __init__(
                self,
                boto3_clients=dict(
                ),
                boto3_session=None,
            ):
        self.boto3_clients = boto3_clients
        self.boto3_session = boto3_session

    def get_boto3_client(
                self,
                client_name,
            ):
        try:
            client = self.boto3_clients[client_name]
        except KeyError:
            assert self.boto3_session

            client = self.boto3_session.client(
                client_name,
            )

            self.boto3_clients[client_name] = client

        return client
