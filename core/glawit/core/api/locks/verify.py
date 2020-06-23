import base64
import json
import logging
import os

import boto3

logger = logging.getLogger(
)


def post(event, context):
    stage_variables = event['stageVariables']

    logging_level = getattr(
        logging,
        stage_variables['logging_level'],
    )

    logger.setLevel(
        logging_level,
    )

    is_base64_encoded = event['isBase64Encoded']

    request_body = event['body']

    if is_base64_encoded:
        logger.debug(
            'request body is Base64-encoded',
        )

        request_body = base64.b64decode(
            request_body,
            validate=True,
        )

    logger.debug(
        'body: %s',
        request_body,
    )

    request_data = json.loads(
        request_body,
    )

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
