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
        owner_name = f'{github_username} ({github_name})'

        existing_lock = glawit.core.locks.try_lock(
            path=request_path,
            owner_name=owner_name,
        )

        if existing_lock:
            status_code = 409
            response_data = {
                'lock': {
                    'id': lock_id,
                    'locked_at': locked_at,
                    'owner': {
                        'name': owner_name,
                    },
                    'path': request_path,
                },
                'message': 'path is already locked',
            }
        else:
            status_code = 201
            response_data = {
                'id': lock_id,
                'locked_at': locked_at,
                'owner': {
                    'name': owner_name,
                },
                'path': request_path,
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
