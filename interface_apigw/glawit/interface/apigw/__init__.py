import logging
import os

import glawit.core.main

logger = logging.getLogger(
)


# Common entry point for Lambda functions invoked by API Gateway
def entry_point(context, event, handler):
    stage_variables = event['stageVariables']

    logging_level = getattr(
        logging,
        stage_variables['logging_level'],
    )

    set_up_logging(
        level=logging_level,
    )

    github_owner = os.environ['GITHUB_OWNER']
    github_repo = os.environ['GITHUB_REPO']

    logger.debug(
        'GitHub repository: %s/%s',
        github_owner,
        github_repo,
    )

    body = event['body']
    headers = event['headers']

    is_base64_encoded = event['isBase64Encoded']

    if is_base64_encoded:
        logger.debug(
            'request body is Base64-encoded',
        )

        body = base64.b64decode(
            body,
            validate=True,
        )

    return_value = glawit.core.main.process_request(
        body=body,
        github_owner=github_owner,
        github_repo=github_repo,
        handler=handler,
        headers=headers,
    )

    return


def set_up_logging(level):
    logger.setLevel(
        logging_level,
    )


def decorator(handler):
    def entry_point_dfd(event, context):
        response = entry_point(
            context=context,
            event=event,
            handler=handler,
        )

        return response

    return entry_point_dfd
