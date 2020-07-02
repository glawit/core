import datetime
import logging

import botocore

import glawit.core.dynamodb

logger = logging.getLogger(
)


def try_lock(boto3_session, github_id, path, ref, table):
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
        'path': path,
    }

    if ref:
        attributes['ref'] = ref

    iterator = attributes.items(
    )

    item = {
        key: glawit.core.dynamodb.value_to_attribute(value)
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
                },
                ReturnConsumedCapacity='NONE',
                TableName=table,
            )

            lock = glawit.core.dynamodb.attributes_to_dict(
                response['Item'],
            )
        else:
            raise e
    else:
        lock_set = True
        lock = attributes

    return (
        lock_set,
        lock,
    )
