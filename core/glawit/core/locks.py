import logging

#import botocore

logger = logging.getLogger(
)


def foobar(session):
    dynamodb = boto3.client(
        'dynamodb',
    )
    return None
