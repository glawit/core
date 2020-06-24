import logging

import glawit.core.access
import glawit.core.locks

logger = logging.getLogger(
)


def get(event, context):
    status_code = 200

    response = {
        'statusCode': status_code,
    }

    return response


def post(config, data, session, viewer_access):
    locktable = config['locktable']

    request_path = data['path']

    try:
        request_ref = data['ref']
    except KeyError:
        pass
    else:
        request_ref_name = request_ref['name']

        logger.debug(
            'refspec: %s',
            request_ref_name,
        )

    if viewer_access >= glawit.core.access.RepositoryAccess.WRITE:
        status_code = 201
        response_data = {
            'id': lock_id,
            'path': request_path,
            'locked_at': locked_at,
            'owner': github_username,
            'owner': github_public_profile_name,
        }

        status_code = 409
        response_data = {
            'lock': {
            },
            'message': 'path is already locked',
        }
    else:
        status_code = 403
        response_data = {
            'message': 'You are not allowed to push to this repository',
        }

    response = {
        'body': response_data,
        'statusCode': status_code,
    }

    return response
