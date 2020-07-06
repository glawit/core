import importlib.resources
import logging

import requests

logger = logging.getLogger(
    __name__,
)


class Error(
            Exception,
        ):
    pass


class QueryError(
            Error,
        ):
    def __init__(
            ):
        pass


def query(
            query_name,
            query_subpackage,
            requests_session,
            url,
            headers={
            },
            variables=None,
        ):
    resource_name = f'{ query_name }.graphql'
    resource_package = f'glawit.core.data.graphql.{ query_subpackage }'

    logger.debug(
        'importing %s from package %s',
        resource_name,
        resource_package,
    )

    query = importlib.resources.read_text(
        encoding='utf-8',
        package=resource_package,
        resource=resource_name,
    )

    data = {
        'query': query,
    }

    if variables:
        data['variables'] = variables

    response = requests_session.post(
        url,
        headers=headers,
        json=data,
    )

    if response.status_code == requests.codes.ok:
        logger.debug(
            'query succeeded',
        )

        response_data = response.json(
        )

        query_result = response_data['data']

        logger.debug(
            'query result: %s',
            query_result,
        )

        return query_result
    else:
        logger.error(
            'query failed',
        )

        e = Exception(
        )

        raise e
