import base64
import json
import logging

import gql
import gql.transport.requests

import glawit

logger = logging.getLogger(
)


def process_request(body, github_owner, github_repo, handler, headers):
    try:
        authorization_header_value = headers['authorization']
    except KeyError:
        logger.error(
            'missing Authorization header',
        )

        response = {
            'statusCode': 401,
            'headers': {
                'Content-Type': 'application/vnd.git-lfs+json',
                'LFS-Authenticate': 'Basic realm="Git LFS", charset="UTF-8"',
            },
            'body': {
                'message': 'Pass your GitHub user as username and a personal token as password',
                'documentation_url': 'https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line',
            },
            'isBase64Encoded': False,
        }
    else:
        logger.debug(
            'Authorization header present',
        )

#        pieces = authorization_header_value.split(
#            maxsplit=1,
#            sep=' ',
#        )
#
#        authorization_type = pieces[0]
#        authorization_credentials = pieces[1]
#
#        logger.debug(
#            'authorization type: %s',
#            authorization_type,
#        )
#
#        token = None
#
#        if authorization_type == 'Basic':
#            logger.debug(
#                'encoded authorization credentials: %s',
#                authorization_credentials,
#            )
#
#            authorization_credentials = base64.b64decode(
#                authorization_credentials,
#                validate=True,
#            )
#
#            authorization_credentials = authorization_credentials.decode(
#                'utf-8',
#            )
#
#            logger.debug(
#                'decoded authorization credentials: %s',
#                authorization_credentials,
#            )
#
#            pieces = authorization_credentials.split(
#                sep=':',
#            )
#
#            username = pieces[0]
#            password = pieces[1]
#
#            logger.debug(
#                'username: %s',
#                username,
#            )
#
#            logger.debug(
#                'password: %s',
#                password,
#            )
#
#            token = password
#        elif authorization_type == 'Token':
#            token = authorization_credentials
#        else:
#            response = {
#                'statusCode': 401,
#                'headers': {
#                    'Content-Type': 'application/vnd.git-lfs+json',
#                    'LFS-Authenticate': 'Basic realm="Git LFS", charset="UTF-8"',
#                },
#                'body': {
#                    'message': 'missing authentication',
#                    # FIXME
#                    'documentation_url': 'https://mo.in/',
#                },
#                'isBase64Encoded': False,
#            }

        transport = gql.transport.requests.RequestsHTTPTransport(
            headers={
                'Authorization': authorization_header_value,
            },
            url='https://api.github.com/graphql',
        )

        client = gql.Client(
            fetch_schema_from_transport=True,
            transport=transport,
        )

        query = gql.gql(
            f'''
                query {{
                    repository( owner : "{github_owner}" , name : "{github_repo}" ) {{
                        viewerPermission
                    }}
                }}
            ''',
        )

        result = client.execute(
            query,
        )

        logger.debug(
            'GitHub query result: %s',
            result,
        )

        viewer_permission = result['repository']['viewerPermission']
        viewer_permission = glawit.RepositoryAccess.READONLY

        if result:
            body_type = type(
                body,
            )

            if body_type == dict:
                data = body
            else:
                # FIXME
                #assert header_says_body_is_json

                logger.debug(
                    'body: %s',
                    body,
                )

                data = json.loads(
                    body,
                )

            config = {
                'github_owner': github_owner,
                'github_repo': github_repo,
                'store_bucket': 'git-lfs.lalala.eu',
            }
            response = handler(
                config=config,
                data=data,
                viewer_permission=viewer_permission,
            )
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

    try:
        body = response['body']
    except KeyError:
        pass
    else:
        body_json = json.dumps(
            body,
        )

        response['body'] = body_json

    return response
