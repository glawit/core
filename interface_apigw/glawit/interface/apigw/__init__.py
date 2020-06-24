import base64
import logging
import os

import glawit.core.main

logger = logging.getLogger(
)

# Top logger object based on whether everything should be logged
top_logger_names = {
    False: 'glawit',
    True: None,
}


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

    config = {
        'github_owner': github_owner,
        'github_repo': github_repo,
        'storage_class': stage_variables['storage_class'],
        'store_bucket': stage_variables['store_bucket'],
    }

    request = {
        'body': body,
        'headers': headers,
    }

    return_value = glawit.core.main.process_request(
        config=config,
        handler=handler,
        request=request,
    )

    return return_value


def set_up_logging(level):
    log_everything = True

    top_logger_name = top_logger_names[log_everything]

    top_logger = logging.getLogger(
        name=top_logger_name,
    )

    top_logger.setLevel(
        level,
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
