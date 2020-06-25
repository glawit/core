import datetime
import logging

#import botocore

logger = logging.getLogger(
)


def try_lock(owner, path, session):
    now = datetime.datetime.now(
        tz=datetime.timezone.utc,
    )

    timestamp = now.isoformat(
        sep='T',
        timespec='seconds',
    )

    dynamodb = boto3.client(
        'dynamodb',
    )


def foobar(session):
    dynamodb = boto3.client(
        'dynamodb',
    )
    return None
