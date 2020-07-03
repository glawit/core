import logging

import glawit.core.s3

logger = logging.getLogger(
    __name__,
)


def post(
            boto3_session,
            config,
            request,
            session,
        ):
    status_code = None

    store_bucket = config['large_file_store']['bucket_name']

    data = request['data']

    oid = data['oid']

    logger.debug(
        'checking object with ID %s',
        oid,
    )

    expected_object_size = data['size']

    logger.debug(
        'expected size: %i bytes',
        expected_object_size,
    )

    object_key = oid

    object_check_result = glawit.core.s3.check_object(
        bucket=store_bucket,
        key=object_key,
        session=boto3_session,
    )

    if object_check_result == -1:
        logger.error(
            'bucket does not contain object with specified ID',
        )

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
                'object on S3 has a different size (%i bytes)',
                object_size,
            )

            status_code = 409

    response = {
        'statusCode': status_code,
    }

    return response
