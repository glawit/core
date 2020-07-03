import logging

import glawit.core.access
import glawit.core.json64

logger = logging.getLogger(
    __name__,
)


def post(
            config,
            request,
            session,
        ):
    viewer_access = session['GitHub']['viewer_access']

    if viewer_access >= glawit.core.access.RepositoryAccess.WRITE:
        locktable = config['locktable']

        data = request['data']

        boto3_session = session['boto3']['session']
        dynamodb = boto3_session.client(
            'dynamodb',
        )

        scan_arguments_ours = dict(
        )
        scan_arguments_theirs = dict(
        )

        try:
            cursors_encoded = data['cursor']
        except KeyError:
            pass
        else:
            cursors = glawit.core.json64.decode(
                cursor_encoded,
            )

            try:
                scan_arguments_ours['ExclusiveStartKey'] = cursors['ours']
            except KeyError:
                pass

            try:
                scan_arguments_theirs['ExclusiveStartKey'] = cursors['theirs']
            except KeyError:
                pass

        try:
            limit_str = data['limit']
        except KeyError:
            limit = config['API']['pagination']['max']
        else:
            limit = min(
                max(
                    max(
                        config['API']['pagination']['min'],
                        2,
                    ),
                    int(
                        limit_str,
                    ),
                ),
                config['API']['pagination']['max'],
            )

        half_limit = limit // 2

        try:
            request_ref = data['ref']
        except KeyError:
            pass
        else:
            ref = request_ref['name']

        next_cursors = dict(
        )

        current_github_user_id = session['GitHub']['id']

        response = dynamodb.scan(
            **scan_arguments_ours,
            ExpressionAttributeValues={
                ':github_id': {
                    'S': current_github_user_id,
                },
            },
            FilterExpression='github_id = :github_id',
            Limit=half_limit,
            ReturnConsumedCapacity='NONE',
            Select='ALL_ATTRIBUTES',
            TableName=locktable,
        )

        items = response['Items']

        github_ids = [
            item['github_id']['S']
            for item in items
        ]

        github_users = glawit.core.github.fetch_users_info(
            graphql_client=session['GitHub']['GraphQL'],
            ids=github_ids,
        )

        ours = [
            {
                'id': item['path']['S'],
                'path': item['path']['S'],
                'locked_at': item['creation_time']['S'],
                'owner': {
                    'name': f'{ github_users[item["github_id"]["S"]]["login"] } ({ github_users[item["github_id"]["S"]]["name"]})',
                },
            }
            for item in items
        ]

        try:
            last_evaluated_key = response['LastEvaluatedKey']
        except KeyError:
            logger.debug(
                'no more results',
            )
        else:
            next_cursors['ours'] = last_evaluated_key

        response = dynamodb.scan(
            **scan_arguments_theirs,
            ExpressionAttributeValues={
                ':github_id': {
                    'S': current_github_user_id,
                },
            },
            FilterExpression='github_id <> :github_id',
            Limit=half_limit,
            ReturnConsumedCapacity='NONE',
            Select='ALL_ATTRIBUTES',
            TableName=locktable,
        )

        items = response['Items']

        github_ids = [
            item['github_id']['S']
            for item in items
        ]

        github_users = glawit.core.github.fetch_users_info(
            graphql_client=session['GitHub']['GraphQL'],
            ids=github_ids,
        )

        theirs = [
            {
                'id': item['path']['S'],
                'path': item['path']['S'],
                'locked_at': item['creation_time']['S'],
                'owner': {
                    'name': f'{ github_users[item["github_id"]["S"]]["login"] } ({ github_users[item["github_id"]["S"]]["name"]})',
                },
            }
            for item in items
        ]

        try:
            last_evaluated_key = response['LastEvaluatedKey']
        except KeyError:
            logger.debug(
                'no more results',
            )
        else:
            next_cursors['theirs'] = last_evaluated_key

        status_code = 200
        response_data = {
            'ours': ours,
            'theirs': theirs,
        }

        if next_cursors:
            response_data['next_cursor'] = glawit.core.json64.encode(
                next_cursors,
            )
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
