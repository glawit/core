import logging
import os

import boto3

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

s3 = boto3.client(
    's3',
)


def post(event, context):
    operation = data['operation']

    bucket = os.environ['Bucket']
    region = os.environ['AWS_REGION']
    storage_class = os.environ['StorageClass']

    s3_method = s3_methods[operation]
    http_method = http_methods[operation]

    request_objects = data['objects']

    response_objects = list(
    )

    for request_object in request_objects:
        oid = request_object['oid']
        size = request_object['size']

        response_object = dict(
        )

        response_object['oid'] = oid
        response_object['size'] = size

        object_key = oid

        object_exists = dfd(
            Bucket=bucket,
            Key=object_key,
        )
        ###
        s3.head_object(
            Bucket=bucket,
            Key=object_key,
        )
        ###

        if operation == 'download':
            if object_exists:
                response_object['authenticated'] = True

                if repository_public:
                    href = f'https://{bucket}.s3.dualstack.{region}.amazonaws.com/{object_key}'

                    expires_in = 2147483647
                else:
                    href = s3.generate_presigned_url(
                        ClientMethod=s3_method,
                        HttpMethod=http_method,
                        Params={
                            'Bucket': bucket,
                            'Key': object_key,
                        },
                        ExpiresIn=50,
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
                    'Bucket': bucket,
                    'Key': object_key,
                    'StorageClass': storage_class,
                },
                ExpiresIn=50,
            )
            action_upload['expires_in'] = 50

            action_verify = dict(
            )

            # FIXME
            action_verify['href'] = foobar
            action_verify['header'] = {
                # FIXME
                'Authorization': f'Bearer {token}',
            }
            #action_verify['expires_in'] 50

            response_object['actions'] = {
                'upload': action_upload,
                'verify': action_verify,
            }

        response_objects.append(
            response_object,
        )

    response_body = {
        'transfer': 'basic',
        'objects': response_objects,
    }

    response_body_json = json.dumps(
        response_body,
    )

    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/vnd.git-lfs+json',
        },
        'body': response_body_json,
        'isBase64Encoded': False,
    }

    return response
