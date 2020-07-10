import logging

logger = logging.getLogger(
    __name__,
)


class Session:
    def __init__(
                self,
                region,
                session,
                clients=[
                ],
            ):
        self.clients = {
        }

        for client_name in clients:
            extra_client_args = {
            }

            # Fix for pre-signed URLs
            if client_name == 's3':
                extra_client_args['endpoint_url'] = f'https://s3.{ region }.amazonaws.com'

            client = session.client(
                client_name,
                region_name=region,
                **extra_client_args,
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
