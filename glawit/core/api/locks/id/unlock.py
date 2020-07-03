import logging

import botocore

import glawit.core.github

logger = logging.getLogger(
    __name__,
)


def post(
            boto3_session,
            config,
            request,
            session,
        ):
    viewer_access = session['GitHub']['viewer_access']

    if viewer_access >= glawit.core.access.RepositoryAccess.WRITE:
        locktable = config['locktable']

        request_data = request['data']
        force = request_data.get(
            'force',
            False,
        )
        lock_id = request['path_variables']['lock_id']

        current_github_user_id = session['GitHub']['id']
        viewer_access = session['GitHub']['viewer_access']

        extra_arguments = {
        }

        if not force:
            extra_arguments['ConditionExpression'] = 'github_id = :github_id'
            extra_arguments['ExpressionAttributeValues'] = {
                ':github_id': {
                    'S': current_github_user_id,
                },
            }

        dynamodb = boto3_session.client(
            'dynamodb',
        )

        try:
            dynamodb_response = dynamodb.delete_item(
                **extra_arguments,
                Key={
                    'path': {
                        'S': lock_id,
                    },
                },
                ReturnConsumedCapacity='NONE',
                ReturnItemCollectionMetrics='NONE',
                ReturnValues='ALL_OLD',
                TableName=locktable,
            )
        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']

            if error_code == 'ConditionalCheckFailedException':
                status_code = 403
                response_data = {
                    'message': 'You did not create the specified lock or it does not exist',
                }
            else:
                raise e
        else:
            try:
                attributes = dynamodb_response['Attributes']
            except KeyError:
                status_code = 404
                response_data = {
                    'message': 'The specified lock does not exist',
                }
            else:
                status_code = 200

                lock_github_id = attributes['github_id']['S']

                github_user = glawit.core.github.fetch_user_info(
                    github_id=lock_github_id,
                    graphql_client=session['GitHub']['GraphQL'],
                )

                response_data = {
                    'lock': {
                        'id': attributes['path']['S'],
                        'path': attributes['path']['S'],
                        'locked_at': attributes['creation_time']['S'],
                        'owner': {
                            'name': f'{ github_user["login"] } ({ github_user["name"] })',
                        },
                    },
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
