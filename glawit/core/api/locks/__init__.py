import base64
import json
import logging

import glawit.core.access
import glawit.core.github
import glawit.core.json64
import glawit.core.locks

logger = logging.getLogger(
)


def get(config, request, session):
    locktable = config['locktable']

    urlparams = request['urlparams']

    boto3_session = session['boto3']['session']

    scan_arguments = {
        'ReturnConsumedCapacity': 'NONE',
        'Select': 'ALL_ATTRIBUTES',
        'TableName': locktable,
    }

    try:
        limit_str = urlparams['limit']
    except KeyError:
        limit = config['API']['max_items']
    else:
        limit = max(
            1,
            int(
                limit_str,
            ),
        )

    scan_arguments['Limit'] = limit

    try:
        cursor = urlparams['cursor']
    except KeyError:
        pass
    else:
        scan_arguments['ExclusiveStartKey'] = glawit.core.json64.decode(
            cursor,
        )

    filter_expressions = list(
    )
    expression_attribute_names = dict(
    )
    expression_attribute_values = dict(
    )

    try:
        lock_id = urlparams['id']
    except KeyError:
        pass
    else:
        expression_attribute_names['#path'] = 'path'

        expression_attribute_values[':lock_id'] = {
            'S': lock_id,
        }

        filter_expression = '#path = :lock_id'

        filter_expressions.append(
            filter_expression,
        )

    try:
        path = urlparams['path']
    except KeyError:
        pass
    else:
        expression_attribute_names['#path'] = 'path'

        expression_attribute_values[':path'] = {
            'S': path,
        }

        filter_expression = '#path = :path'

        filter_expressions.append(
            filter_expression,
        )

    try:
        ref = urlparams['refspec']
    except KeyError:
        pass
    else:
        expression_attribute_names['#ref'] = 'ref'

        expression_attribute_values[':ref'] = {
            'S': ref,
        }

        filter_expression = '#ref = :ref'

        filter_expressions.append(
            filter_expression,
        )

    if filter_expressions:
        scan_arguments['ExpressionAttributeNames'] = expression_attribute_names

        scan_arguments['ExpressionAttributeValues'] = expression_attribute_values

        filter_expression = ' and '.join(
            filter_expressions,
        )

        scan_arguments['FilterExpression'] = filter_expression

    dynamodb = boto3_session.client(
        'dynamodb',
    )

    response = dynamodb.scan(
        **scan_arguments,
    )

    status_code = 200

    items = response['Items']

    github_ids = [
        item['github_id']['S']
        for item in items
    ]

    github_users = glawit.core.github.fetch_users_info(
        graphql_client=session['GitHub']['GraphQL'],
        ids=github_ids,
    )

    response_data = {
        'locks': [
            {
                'id': item['path']['S'],
                'path': item['path']['S'],
                'locked_at': item['creation_time']['S'],
                'owner': {
                    'name': f'{ github_users[item["github_id"]["S"]]["login"] } ({ github_users[item["github_id"]["S"]]["name"] })',
                },
            }
            for item in items
        ],
    }

    try:
        last_evaluated_key = response['LastEvaluatedKey']
    except KeyError:
        logger.debug(
            'no more results',
        )
    else:
        response_data['next_cursor'] = glawit.core.json64.encode(
            last_evaluated_key,
        )

    response = {
        'body': response_data,
        'headers': {
            'Content-Type': 'application/vnd.git-lfs+json',
        },
        'statusCode': status_code,
    }

    return response


def post(config, request, session):
    viewer_access = session['GitHub']['viewer_access']

    if viewer_access >= glawit.core.access.RepositoryAccess.WRITE:
        locktable = config['locktable']

        request_data = request['data']
        request_path = request_data['path']

        boto3_session = session['boto3']['session']

        try:
            request_ref = request_data['ref']
        except KeyError:
            ref = ''
        else:
            ref = request_ref['name']

        logger.debug(
            'ref: %s',
            ref,
        )
        updated, lock = glawit.core.locks.try_lock(
            boto3_session=boto3_session,
            github_id=session['GitHub']['id'],
            path=request_path,
            ref=ref,
            table=config['locktable'],
        )

        lock_github_id = lock['github_id']

        github_user = glawit.core.github.fetch_user_info(
            graphql_client=session['GitHub']['GraphQL'],
            id=lock_github_id,
        )

        lock_github_username = github_user['login']
        lock_github_name = github_user['name']

        owner_name = f'{ lock_github_username } ({ lock_github_name })'

        if updated:
            status_code = 201

            response_data = {
                'id': lock['path'],
                'locked_at': lock['creation_time'],
                'owner': {
                    'name': owner_name,
                },
                'path': request_path,
            }
        else:
            status_code = 409
            response_data = {
                'lock': {
                    'id': lock['path'],
                    'locked_at': lock['creation_time'],
                    'owner': {
                        'name': owner_name,
                    },
                    'path': request_path,
                },
                'message': 'path is already locked',
            }
    else:
        status_code = 403
        response_data = {
            'message': 'You are not allowed to push to this repository',
        }

    response = {
        'body': response_data,
        'headers': {
            'Content-Type': 'application/vnd.git-lfs+json',
        },
        'statusCode': status_code,
    }

    return response
