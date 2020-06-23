import json
import logging

import boto3

logger = logging.getLogger(
)


def post(event, context):
    try:
        ref = request_data['ref']
        refname = ref['name']
    except KeyError:
        pass

    limit = request_data.get(
        'limit',
        100,
    )

    response_data = {
        'ours': list(
        ),
        'theirs': list(
        ),
    }

    if True:
        response_data['next_cursor'] = next_cursor

    response_body = json.dumps(
        response_data,
    )

    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/vnd.git-lfs+json',
        },
        'body': response_body,
        'isBase64Encoded': False,
    }

    return response
