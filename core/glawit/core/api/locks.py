import logging

import boto3

logger = logging.getLogger(
)

dynamodb = boto3.client(
    'dynamodb',
)


def get(event, context):
    status_code = 200

    response = {
        'statusCode': status_code,
    }

    return response


def post(event, context):
    status_code = 200

    response = {
        'statusCode': status_code,
    }

    return response
