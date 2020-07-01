import logging

import glawit.core.access

logger = logging.getLogger(
)


def post(boto3_session, config, github, request):
    viewer_access = github['viewer_access']

    if viewer_access >= glawit.core.access.RepositoryAccess.WRITE:
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
