import importlib.resources
import logging

import gql


def fetch_user_info(graphql_client, id):
    graphql_query_code = importlib.resources.read_text(
        encoding='utf-8',
        package='glawit.core.data.graphql',
        resource='users.graphql',
    )

    graphql_query = gql.gql(
        graphql_query_code,
    )

    graphql_query_variables = {
        'ids': [
            id,
        ],
    }

    result = graphql_client.execute(
        document=graphql_query,
        variable_values=graphql_query_variables,
    )

    nodes = result['nodes']

    node = nodes[0]

    return node


def fetch_users_info(graphql_client, ids):
    graphql_query_code = importlib.resources.read_text(
        encoding='utf-8',
        package='glawit.core.data.graphql',
        resource='users.graphql',
    )

    graphql_query = gql.gql(
        graphql_query_code,
    )

    graphql_query_variables = {
        'ids': ids,
    }

    result = graphql_client.execute(
        document=graphql_query,
        variable_values=graphql_query_variables,
    )

    nodes_list = result['nodes']

    nodes = {
        node['id']: node
        for node in nodes_list
    }

    return nodes
