import base64
import json
import logging


def decode(token):
    token_bytes = base64.urlsafe_b64decode(
        token,
    )

    token_json = token_bytes.decode(
        encoding='utf-8',
    )

    data = json.loads(
        token_json,
    )

    return data


def encode(data):
    token_json = json.dumps(
        data,
    )

    token_bytes = token_json.encode(
        encoding='utf-8',
    )

    token_bytes_base64 = base64.urlsafe_b64encode(
        token_bytes,
    )

    token = token_bytes_base64.decode(
        encoding='utf-8',
    )

    return token
