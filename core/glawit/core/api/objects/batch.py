import logging

import glawit.core.access
import glawit.core.s3

logger = logging.getLogger(
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


def post(config, data, session, viewer_access):
    s3 = session.client(
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
        pass
    else:
        logger.debug(
            'transfer adapters: %s',
            request_transfers,
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

    for request_object in request_objects:
        request_object_oid = request_object['oid']
        request_object_size = request_object['size']

        response_object = dict(
        )

        response_object['oid'] = request_object_oid

        object_key = request_object_oid

        object_check_result = glawit.core.s3.check_object(
            bucket=store_bucket,
            key=object_key,
            session=session,
        )

        object_exists = object_check_result != -1

        if operation == 'download':
            if object_exists:
                object_size = object_check_result

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
                    response_object['error'] = {
                        'code': 409,
                        'message': 'Object on the server has the same ID but different size',
                    }
            else:
                response_object['error'] = {
                    'code': 404,
                    'message': 'Object does not exist',
                }

        elif operation == 'upload' and not object_exists:
            response_object['authenticated'] = True

            action_upload = dict(
            )

            action_upload['href'] = s3.generate_presigned_url(
                ClientMethod=s3_method,
                HttpMethod=http_method,
                Params={
                    'Bucket': store_bucket,
                    'Key': object_key,
                    'StorageClass': storage_class,
                },
                ExpiresIn=50,
            )

            action_upload['expires_in'] = 50

            action_verify = dict(
            )

            action_verify['href'] = f'{api_endpoint}/verify'
            # FIXME
            action_verify['header'] = {
                #'Authorization': f'Bearer {token}',
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
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/vnd.git-lfs+json',
        },
        'body': response_data,
        'isBase64Encoded': False,
    }

    return response
