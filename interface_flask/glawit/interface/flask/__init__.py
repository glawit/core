import logging

import boto3
import flask
import werkzeug.datastructures

import glawit.core.api.locks
import glawit.core.api.locks.id.unlock
import glawit.core.api.locks.verify
import glawit.core.api.objects.batch
import glawit.core.api.verify
import glawit.core.main

logger = logging.getLogger(
)

app = flask.Flask(
    __name__,
)
# FIXME
app.config['api_endpoint'] = 'http://127.0.0.1:5000'
app.config['aws_region'] = 'eu-central-1'
app.config['github_owner'] = 'kalrish'
app.config['github_repo'] = 'music'
app.config['store_bucket'] = 'git-lfs-apis-playground-store-bucket-1p2f8sde4jq8g'
app.config['storage_class'] = 'STANDARD'
session = boto3.session.Session(
)

config = {
    'API': {
        'endpoint': app.config['api_endpoint'],
    },
    'AWS': {
        'region': app.config['aws_region'],
    },
    'GitHub': {
        'owner': app.config['github_owner'],
        'repo': app.config['github_repo'],
    },
    'large_file_store': {
        'bucket_name': app.config['store_bucket'],
        'storage_class': app.config['storage_class'],
    },
}


@app.route(
    '/locks',
    methods=[
        'GET',
        'POST',
    ],
)
def locks():
    if flask.request.method == 'GET':
        response = glawit.api.locks.get(
        )
    else:
        assert flask.request.method == 'POST'

        response = glawit.api.locks.post(
        )

    return response


@app.route(
    '/locks/verify',
    methods=[
        'POST',
    ],
)
def locks_verify():
    response = glawit.api.locks.verify.post(
    )

    return response


@app.route(
    '/locks/<id>/unlock',
    methods=[
        'POST',
    ],
)
def locks_id_unlock(id):
    response = glawit.main.galwit(
        data=data,
        github_owner=app.config['github_owner'],
        github_repo=app.config['github_repo'],
        handler=glawit.api.locks.id.unlock.post,
        headers=flask.request.headers,
    )

    return response


@app.route(
    '/objects/batch',
    methods=[
        'POST',
    ],
)
def objects_batch():
    request = {
        'data': flask.request.json,
        'headers': flask.request.headers,
    }

    response = glawit.core.main.process_request(
        config=config,
        handler=glawit.core.api.objects.batch.post,
        request=request,
        session=session,
    )

#    resp = flask.Response(
#        headers=werkzeug.datastructures.Headers(
#            response.get(
#                'headers',
#                dict(
#                ),
#            ),
#        ),
#        status=response['statusCode'],
#    )

    return (
        response['body'],
        response['statusCode'],
        response['headers'],
    )


@app.route(
    '/verify',
    methods=[
        'GET',
        'POST',
    ],
)
def verify():
    request = {
        'data': flask.request.json,
        'headers': flask.request.headers,
    }

    response = glawit.core.main.process_request(
        config=config,
        handler=glawit.core.api.verify.post,
        request=request,
        session=session,
    )

    resp = flask.Response(
        headers=werkzeug.datastructures.Headers(
            response.get(
                'headers',
                dict(
                ),
            ),
        ),
        status=response['statusCode'],
    )

    return resp
