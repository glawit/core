import logging

import glawit.core.access
import glawit.core.s3

logger = logging.getLogger(
    __name__,
)

allowed_viewer_permissions_upload = {
    'ADMIN',
    'MAINTAIN',
    'WRITE',
}

s3_methods = {
    'download': 'get_object',
    'upload': 'put_object',
}

http_methods = {
    'download': 'GET',
    'upload': 'PUT',
}


def post(config, request, session):
    boto3_session = session['boto3']['session']
    viewer_access = session['GitHub']['viewer_access']

    data = request['data']
    request_headers = request['headers']


    s3 = boto3_session.client(
        's3',
    )


    # FIXME
    repository_public = False
    api_endpoint = config['API']['endpoint']
    aws_region = config['AWS']['region']
    store_bucket = config['large_file_store']['bucket_name']
    storage_class = config['large_file_store']['storage_class']


    request_objects = data['objects']
    request_operation = data['operation']

    logger.debug(
        'operation: %s',
        request_operation,
    )

    logger.debug(
        'amount of objects specified: %i',
        len(
            request_objects,
        ),
    )

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

    try:
        request_transfers = data['transfers']
    except KeyError:
        logger.debug(
            'client did not specify any transfer adapter; assuming "basic"',
        )
    else:
        logger.debug(
            'client specified these transfer adapters: %s',
            ', '.join(
                request_transfers,
            ),
        )

        transfer_basic_passed = False
        for request_transfer in request_transfers:
            if request_transfer == 'basic':
                transfer_basic_passed = True
                break

        # FIXME: turn into proper HTTP response
        assert transfer_basic_passed


    s3_method = s3_methods[request_operation]
    http_method = http_methods[request_operation]


    response_objects = list(
    )

    iterator = enumerate(
        request_objects,
        start=1,
    )

    for object_index, request_object in iterator:
        request_object_oid = request_object['oid']

        logger.debug(
            'object #%i: OID: %s',
            object_index,
            request_object_oid,
        )

        request_object_size = request_object['size']

        logger.debug(
            'object #%i: size: %i bytes',
            object_index,
            request_object_size,
        )

        response_object = dict(
        )

        response_object['oid'] = request_object_oid

        object_key = request_object_oid

        object_check_result = glawit.core.s3.check_object(
            bucket=store_bucket,
            key=object_key,
            session=boto3_session,
        )

        object_exists = object_check_result != -1

        if object_exists:
            object_size = object_check_result

        if request_operation == 'download':
            if object_exists:
                logger.debug(
                    'object #%i: exists',
                    object_index,
                )

                response_object['size'] = object_size

                if object_size == request_object_size:
                    # All URLs returned include authorization
                    response_object['authenticated'] = True

                    if repository_public:
                        href = f'https://{store_bucket}.s3.dualstack.{aws_region}.amazonaws.com/{object_key}'

                        expires_in = 2147483647
                    else:
                        href = s3.generate_presigned_url(
                            ClientMethod=s3_method,
                            HttpMethod=http_method,
                            Params={
                                'Bucket': store_bucket,
                                'Key': object_key,
                            },
                            ExpiresIn=50,
                        )

                        logger.debug(
                            'bucket %s: key %s: pre-signed download URL: %s',
                            store_bucket,
                            object_key,
                            href,
                        )

                        expires_in = 45

                    response_object['actions'] = {
                        'download': {
                            'href': href,
                            'expires_in': expires_in,
                        },
                    }
                else:
                    logger.error(
                        'object #%i: object on S3 has a different size (%i)',
                        object_index,
                        object_size,
                    )

                    response_object['error'] = {
                        'code': 409,
                        'message': 'Object on the server has the same ID but different size',
                    }
            else:
                logger.error(
                    'object #%i: does not exist',
                    object_index,
                )

                response_object['error'] = {
                    'code': 404,
                    'message': 'Object does not exist',
                }

        elif request_operation == 'upload':
            if object_exists:
                if object_size == request_object_size:
                    logger.info(
                        'object #%i: already present on S3',
                        object_index,
                    )
                else:
                    logger.error(
                        'object #%i: object on S3 has a different size (%i)',
                        object_index,
                        object_size,
                    )

                    response_object['error'] = {
                        'code': 409,
                        'message': 'Object on the server has a different size',
                    }
            else:
                logger.info(
                    'object #%i: does not exist; must be uploaded',
                    object_index,
                )

                response_object['size'] = request_object_size
                response_object['authenticated'] = True

                action_upload = dict(
                )

                upload_url = s3.generate_presigned_url(
                    ClientMethod=s3_method,
                    HttpMethod=http_method,
                    Params={
                        'Bucket': store_bucket,
                        'Key': object_key,
                        'StorageClass': storage_class,
                    },
                    ExpiresIn=3600,
                )

                logger.info(
                    'object #%i: upload URL: %s',
                    object_index,
                    upload_url,
                )

                action_upload['href'] = upload_url

                action_upload['header'] = {
                    'x-amz-storage-class': storage_class,
                }

                action_upload['expires_in'] = 3600

                action_verify = dict(
                )

                action_verify['href'] = f'{api_endpoint}/verify'
                action_verify['header'] = {
                    'Authorization': request_headers['authorization'],
                }
                action_verify['expires_in'] = 2147483647

                response_object['actions'] = {
                    'upload': action_upload,
                    'verify': action_verify,
                }

        response_objects.append(
            response_object,
        )

    response_data = {
        'transfer': 'basic',
        'objects': response_objects,
    }

    response = {
        'body': response_data,
        'headers': {
            'Content-Type': 'application/vnd.git-lfs+json',
        },
        'statusCode': 200,
    }

    return response
