import json
import logging

import glawit.core.access
import glawit.core.github
import glawit.core.graphql

logger = logging.getLogger(
    __name__,
)


def process_request(
            boto3_session,
            config,
            handler,
            request,
            requests_session,
        ):
    headers = request['headers']

    try:
        authorization_header_value = headers['authorization']
    except KeyError:
        logger.error(
            'missing Authorization header',
        )

        response = {
            'body': {
                'message': 'Pass your GitHub user as username and a personal token as password',
                'documentation_url': 'https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line',
            },
            'headers': {
                'Content-Type': 'application/vnd.git-lfs+json',
                'LFS-Authenticate': 'Basic realm="Git LFS", charset="UTF-8"',
            },
            'statusCode': 401,
        }
    else:
        logger.debug(
            'Authorization header present',
        )

        github_owner = config['GitHub']['owner']
        github_repo = config['GitHub']['repo']

        try:
            result = glawit.core.github.query(
                authorization_header_value=authorization_header_value,
                query_name='main',
                requests_session=requests_session,
                variables={
                    'owner': github_owner,
                    'repo': github_repo,
                },
            )
        except glawit.core.graphql.QueryError:
            response = {
                'body': {
                    'message': 'The GitHub API token provided lacks access to this GitHub repository.',
                    # FIXME
                    'documentation_url': 'https://mo.in/',
                },
                'headers': {
                    'Content-Type': 'application/vnd.git-lfs+json',
                },
                'statusCode': 403,
            }
        else:
            result_repository = result['repository']
            if result_repository:
                viewer_permission = result_repository['viewerPermission']

                viewer_access = glawit.core.access.RepositoryAccess[viewer_permission]

                # FIXME
                minimum_access_setting = 'ADMIN'
                minimum_access = glawit.core.access.RepositoryAccess[minimum_access_setting]

                enough = viewer_access >= minimum_access

                if enough:
                    if 'data' not in request:
                        try:
                            body = request['body']
                        except KeyError:
                            pass
                        else:
                            # FIXME: check value of Content-Type header

                            logger.debug(
                                'body: %s',
                                body,
                            )

                            data = json.loads(
                                body,
                            )

                            request['data'] = data

                    github_id = result['viewer']['id']

                    logger.info(
                        'GitHub ID: %s',
                        github_id,
                    )

                    session = {
                        'GitHub': {
                            'authorization_header_value': authorization_header_value,
                            'id': github_id,
                            'viewer_access': viewer_access,
                        },
                    }

                    response = handler(
                        boto3_session=boto3_session,
                        config=config,
                        request=request,
                        session=session,
                        requests_session=requests_session,
                    )
                else:
                    response = {
                        'body': {
                            'message': 'Your permission level for this repository is not enough.',
                            'documentation_url': 'https://help.github.com/en/github/getting-started-with-github/access-permissions-on-github',
                        },
                        'headers': {
                            'Content-Type': 'application/vnd.git-lfs+json',
                        },
                        'statusCode': 403,
                    }
            else:
                response = {
                    'body': {
                        'message': 'It seems the GitHub repository is private and the GitHub API token provided lacks access to private repositories. Grant it the corresponding scope and try again.',
                        'documentation_url': 'https://developer.github.com/apps/building-oauth-apps/understanding-scopes-for-oauth-apps/#available-scopes',
                    },
                    'headers': {
                        'Content-Type': 'application/vnd.git-lfs+json',
                    },
                    'statusCode': 403,
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
