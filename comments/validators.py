
import nh3
from defusedxml import ElementTree
from rest_framework import serializers


ALLOWED_TAGS = {"a", "code", "i", "strong"}


def validate_comment_html(value):
    try:
        root = ElementTree.fromstring(
            f"<root>{value}</root>"
        )
    except ElementTree.ParseError:
        raise serializers.ValidationError(
            "HTML tags must be properly closed"
        )

    for element in root.iter():
        if element is root:
            continue

        if element.tag not in ALLOWED_TAGS:
            raise serializers.ValidationError(
                f"Tag <{element.tag}> is not allowed"
            )

        allowed_attrs = ({"href", "title"} if element.tag == "a" else set())

        if set(element.attrib) - allowed_attrs:
            raise serializers.ValidationError(
                "Invalid HTML attributes"
            )

    cleaned = nh3.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes={"a": {"href", "title"}},
        url_schemes={"http", "https", "mailto"},
    )

    return cleaned
