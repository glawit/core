import flask
import werkzeug.datastructures

import glawit.api.locks
import glawit.api.locks.id.unlock
import glawit.api.locks.verify
import glawit.api.objects.batch
import glawit.api.verify
import glawit.main

app = flask.Flask(
    __name__,
)
app.config['github_owner'] = 'kalrish'
app.config['github_repo'] = 'music'


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
    response = glawit.api.objects.batch.post(
    )

    return response


@app.route(
    '/verify',
    methods=[
        'GET',
        'POST',
    ],
)
def verify():
    response = glawit.main.galwit(
        body=flask.request.json,
        github_owner=app.config['github_owner'],
        github_repo=app.config['github_repo'],
        handler=glawit.api.verify.post,
        headers=flask.request.headers,
    )

    resp = flask.Response(
        headers=werkzeug.datastructures.Headers(
            response['headers'],
        ),
        status=response['statusCode'],
    )

    return resp
