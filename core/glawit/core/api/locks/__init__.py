import base64
import json
import logging

import glawit.core.access
import glawit.core.locks

logger = logging.getLogger(
)


def get(boto3_session, config, github, request):
    locktable = config['locktable']

    data = request['data']
    urlparams = request['urlparams']

    scan_arguments = {
        'ReturnConsumedCapacity': 'NONE',
        'Select': 'ALL_ATTRIBUTES',
        'TableName': locktable,
    }

    try:
        limit_str = urlparams['limit']
    except KeyError:
        limit = 100
    else:
        limit = int(
            limit_str,
        )

    scan_arguments['Limit'] = limit

    try:
        cursor = urlparams['cursor']
    except KeyError:
        pass
    else:
        cursor_bytes = base64.urlsafe_b64decode(
            cursor,
        )
        cursor_json = cursor_bytes.decode(
            encoding='utf-8',
        )
        last_evaluated_key = json.loads(
            cursor_json,
        )
        scan_arguments['ExclusiveStartKey'] = last_evaluated_key

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

    response_data = {
        'locks': [
            {
                'id': item['path']['S'],
                'path': item['path']['S'],
                'locked_at': item['creation_time']['S'],
                'owner': {
                    'name': f'{ item["github_username"]["S"] } ({ item["github_name"]["S"]})',
                },
            }
            for item in response['Items']
        ],
    }

    try:
        last_evaluated_key = response['LastEvaluatedKey']
    except KeyError:
        logger.debug(
            'no more results',
        )
    else:
        next_cursor_json = json.dumps(
            last_evaluated_key,
        )
        next_cursor_bytes = next_cursor_json.encode(
            encoding='utf-8',
        )
        next_cursor_bytes_base64 = base64.urlsafe_b64encode(
            next_cursor_bytes,
        )
        next_cursor = next_cursor_bytes_base64.decode(
            encoding='utf-8',
        )
        response_data['next_cursor'] = next_cursor

    response = {
        'body': response_data,
        'headers': {
            'Content-Type': 'application/vnd.git-lfs+json',
        },
        'statusCode': status_code,
    }

    return response


def post(boto3_session, config, github, request):
    viewer_access = github['viewer_access']

    if viewer_access >= glawit.core.access.RepositoryAccess.WRITE:
        locktable = config['locktable']

        data = request['data']

        request_path = data['path']

        try:
            request_ref = data['ref']
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
            github_id=github['id'],
            github_name=github['name'],
            github_username=github['username'],
            path=request_path,
            ref=ref,
            table=config['locktable'],
        )

        lock_github_name = lock['github_name']
        lock_github_username = lock['github_username']
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
