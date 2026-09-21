#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


class WebflowToAirbyteMapping:

    """
    The following disctionary is used for dynamically pulling the schema from Webflow, and mapping it to an Airbyte-compatible json-schema
        Webflow: https://developers.webflow.com/#get-collection-with-full-schema
        Airbyte/json-schema:  https://docs.airbyte.com/understanding-airbyte/supported-data-types/
    """

    # Field type names per Webflow API v2 "Get Collection" response -
    # https://developers.webflow.com/data/reference/cms/collections/get
    webflow_to_airbyte_mapping = {
        "Switch": {"type": ["null", "boolean"]},
        "DateTime": {
            "type": ["null", "string"],
            "format": "date-time",
        },
        "Email": {
            "type": ["null", "string"],
        },
        "Phone": {
            "type": ["null", "string"],
        },
        "Image": {"type": ["null", "object"], "additionalProperties": True},
        "MultiImage": {"type": ["null", "array"]},
        "Reference": {"type": ["null", "string"]},
        "MultiReference": {"type": ["null", "array"]},
        "Link": {"type": ["null", "string"]},
        "Color": {"type": ["null", "string"]},
        "Number": {"type": ["null", "number"]},
        "Option": {"type": ["null", "string"]},
        "PlainText": {"type": ["null", "string"]},
        "RichText": {"type": ["null", "string"]},
        "VideoLink": {"type": ["null", "string"]},
        "File": {"type": ["null", "object"], "additionalProperties": True},
        "ExtFileRef": {"type": ["null", "object"], "additionalProperties": True},
    }
