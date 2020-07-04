import logging

logger = logging.getLogger(
    __name__,
)


class Session:
    def __init__(
                self,
                session,
                clients=[
                ],
            ):
        self.clients = {
        }

        for client_name in clients:
            client = session.client(
                client_name,
            )

            logger.debug(
                '%s client created',
                client_name,
            )

            self.clients[client_name] = client

        self.session = session

    def client(
                self,
                client_name,
            ):
        try:
            client = self.clients[client_name]
        except KeyError:
            logger.debug(
                'client %s not found in cache',
                client_name,
            )

            client = self.session.client(
                client_name,
            )

            self.clients[client_name] = client
        else:
            logger.debug(
                'client %s found in cache',
                client_name,
            )

        return client
