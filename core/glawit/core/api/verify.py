import logging

import glawit.core.access
import glawit.core.s3

logger = logging.getLogger(
)


def post(config, data, session, viewer_access):
    status_code = None

    bucket = config['store_bucket']

    oid = data['oid']
    expected_object_size = data['size']

    object_key = oid

    object_check_result = glawit.core.s3.check_object(
        bucket=bucket,
        key=object_key,
        session=session,
    )

    if object_check_result == -1:
        # bucket does not contain object with that key

        status_code = 404
    else:
        object_size = object_check_result

        if expected_object_size == object_size:
            logger.debug(
                'size matches',
            )

            status_code = 200
        else:
            logger.error(
                'size does not match; client expected %i',
                expected_object_size,
            )

            status_code = 409

    if False:
        if viewer_permission >= glawit.core.access.RepositoryAccess.READONLY:
            assert True
        else:
            response = {
                'statusCode': 403,
                'headers': {
                    'Content-Type': 'application/vnd.git-lfs+json',
                },
                'body': {
                    'message': 'forbidden',
                    # FIXME
                    'documentation_url': 'https://mo.in/',
                },
                'isBase64Encoded': False,
            }

    response = {
        'statusCode': status_code,
    }

    return response
