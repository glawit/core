import logging

import glawit.core.graphql

graphql_endpoint = 'https://api.github.com/graphql'

logger = logging.getLogger(
    __name__,
)


def query(
            authorization_header_value,
            query_name,
            requests_session,
            variables=None,
        ):
    result = glawit.core.graphql.query(
        headers={
            'Authorization': authorization_header_value,
        },
        query_name=query_name,
        query_subpackage='github',
        url=graphql_endpoint,
        variables=variables,
    )

    return result


def fetch_user_info(
            authorization_header_value,
            github_id,
            requests_session,
        ):
    nodes = query_user_nodes(
        authorization_header_value=authorization_header_value,
        github_ids=[
            github_id,
        ],
        requests_session=requests_session,
    )

    node = nodes[0]

    node_id = node['id']

    logger.debug(
        '%s: username: %s',
        node_id,
        node['login'],
    )

    logger.debug(
        '%s: name: %s',
        node_id,
        node['name'],
    )

    return node


def fetch_users_info(
            authorization_header_value,
            github_ids,
            requests_session,
        ):
    nodes_list = query_user_nodes(
        authorization_header_value=authorization_header_value,
        github_ids=github_ids,
        requests_session=requests_session,
    )

    nodes = {
        node['id']: node
        for node in nodes_list
    }

    return nodes


def query_user_nodes(
            authorization_header_value,
            github_ids,
            requests_session,
        ):
    result = query(
        authorization_header_value=authorization_header_value,
        query_name='users',
        requests_session=requests_session,
        variables={
            'ids': github_ids,
        },
    )

    nodes = result['nodes']

    return nodes
