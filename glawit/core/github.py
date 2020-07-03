import importlib.resources
import logging

import gql

logger = logging.getLogger(
    __name__,
)


def fetch_user_info(
            github_id,
            graphql_client,
        ):
    nodes = query_user_nodes(
        github_ids=[
            github_id,
        ],
        graphql_client=graphql_client,
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
            github_ids,
            graphql_client,
        ):
    nodes_list = query_user_nodes(
        github_ids=github_ids,
        graphql_client=graphql_client,
    )

    nodes = {
        node['id']: node
        for node in nodes_list
    }

    return nodes


def query_user_nodes(
            github_ids,
            graphql_client,
        ):
    graphql_query_code = importlib.resources.read_text(
        encoding='utf-8',
        package='glawit.core.data.graphql',
        resource='users.graphql',
    )

    graphql_query = gql.gql(
        graphql_query_code,
    )

    graphql_query_variables = {
        'ids': github_ids,
    }

    result = graphql_client.execute(
        document=graphql_query,
        variable_values=graphql_query_variables,
    )

    nodes = result['nodes']

    return nodes
