import logging

logger = logging.getLogger(
)


def value_to_attribute(value):
    value_type = type(
        value,
    )

    assert value_type == str

    value_dict = {
        'S': value,
    }

    return value_dict


def attributes_to_dict(attributes):
    iterator = attributes.items(
    )

    attributes_dict = {
        attribute_key: attribute_value['S']
        for attribute_key, attribute_value in iterator
    }

    return attributes_dict
