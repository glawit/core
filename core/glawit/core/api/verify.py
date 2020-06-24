import logging

import boto3
import botocore

import glawit.core.access

logger = logging.getLogger(
)

s3 = boto3.client(
    's3',
)


def post(config, data, viewer_access):
    bucket = config['store_bucket']

    oid = data['oid']
    expected_size = data['size']

    object_key = oid

    try:
        s3_response = s3.head_object(
            Bucket=bucket,
            Key=object_key,
        )
    #except s3.exceptions.NoSuchKey:
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            logger.warning(
                'bucket %s does not have object with key %s',
                bucket,
                object_key,
            )

            response = {
                'statusCode': 404,
            }
        else:
            raise e
    else:
        s3_object_size = s3_response['ContentLength']

        logger.debug(
            'bucket %s has object with key %s and size %i',
            bucket,
            object_key,
            s3_object_size,
        )

        if expected_size == s3_object_size:
            logger.debug(
                'size matches',
            )

            response = {
                'statusCode': 200,
            }
        else:
            logger.error(
                'size does not match; client expected %i',
                expected_size,
            )

            response = {
                'statusCode': 409,
            }

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

    return response
