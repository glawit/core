import datetime
import logging

import botocore

logger = logging.getLogger(
)


def try_lock(boto3_session, github_id, github_name, github_username, path, ref, table):
    #if not ref:
    #    ref = '-'

    now = datetime.datetime.now(
        tz=datetime.timezone.utc,
    )

    timestamp = now.isoformat(
        sep='T',
        timespec='seconds',
    )

    attributes = {
        'creation_time': timestamp,
        'github_id': github_id,
        'github_name': github_name,
        'github_username': github_username,
        'path': path,
        #'ref': ref,
    }

    if ref:
        attributes['ref'] = ref

    iterator = attributes.items(
    )

    item = {
        key: value_to_value_dict(value)
        for key, value in iterator
    }

    dynamodb = boto3_session.client(
        'dynamodb',
    )

    try:
        response = dynamodb.put_item(
            ConditionExpression='attribute_not_exists(#path)',
            ExpressionAttributeNames={
                '#path': 'path',
            },
            Item=item,
            ReturnConsumedCapacity='NONE',
            ReturnItemCollectionMetrics='NONE',
            ReturnValues='NONE',
            TableName=table,
        )
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']

        if error_code == 'ConditionalCheckFailedException':
            logger.info(
                'path %s: already locked',
                path,
            )

            lock_set = False

            response = dynamodb.get_item(
                Key={
                    'path': {
                        'S': path,
                    },
                    'ref': {
                        'S': ref,
                    },
                },
                ReturnConsumedCapacity='NONE',
                TableName=table,
            )

            attributes = response['Item']
            lock = {
                attribute_key: attribute_data['S']
                for attribute_key, attribute_data in attributes.items()
            }
        else:
            raise e
    else:
        lock_set = True
        lock = attributes

    return (
        lock_set,
        lock,
    )


def value_to_value_dict(value):
    value_type = type(
        value,
    )

    assert value_type == str

    value_dict = {
        'S': value,
    }

    return value_dict
