import logging

import botocore

logger = logging.getLogger(
    __name__,
)


def check_object(bucket, key, session):
    return_value = None

    s3 = session.client(
        's3',
    )

    try:
        s3_response = s3.head_object(
            Bucket=bucket,
            Key=key,
        )
    # except s3.exceptions.NoSuchKey:
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']

        logger.debug(
            'bucket %s: key %s: HeadObject: %s',
            bucket,
            key,
            error_code,
        )

        if error_code == '404':
            logger.debug(
                'bucket %s: key %s: absent',
                bucket,
                key,
            )

            return_value = -1
        else:
            raise e
    else:
        logger.debug(
            'bucket %s: key %s: present',
            bucket,
            key,
        )

        object_size = s3_response['ContentLength']

        logger.debug(
            'bucket %s: key %s: size: %i bytes',
            bucket,
            key,
            object_size,
        )

        return_value = object_size

    assert return_value

    return return_value
