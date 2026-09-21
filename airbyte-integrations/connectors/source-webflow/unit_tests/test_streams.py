#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_webflow.source import CollectionContents, CollectionSchema, SourceWebflow, WebflowStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(WebflowStream, "path", "v0/example_endpoint")
    mocker.patch.object(WebflowStream, "primary_key", "test_primary_key")
    mocker.patch.object(WebflowStream, "__abstractmethods__", set())


def test_request_params_of_collection_items(patch_base_class):
    stream = CollectionContents()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"offset": 1}}
    expected_params = {"limit": 100, "offset": 1}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token_of_collection_items(patch_base_class):
    stream = CollectionContents()
    response_data = {
        "items": [{"item1_key": "item1_val"}],
        "pagination": {"limit": 10, "offset": 100, "total": 200},
    }
    inputs = {"response": MagicMock(json=lambda: response_data)}
    expected_token = {"offset": 110}
    assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token_of_collection_items_stops_when_exhausted(patch_base_class):
    stream = CollectionContents()
    response_data = {
        "items": [{"item1_key": "item1_val"}],
        "pagination": {"limit": 10, "offset": 190, "total": 200},
    }
    inputs = {"response": MagicMock(json=lambda: response_data)}
    assert stream.next_page_token(**inputs) == {}


def test_next_page_token_of_collection_items_stops_when_no_items(patch_base_class):
    stream = CollectionContents()
    response_data = {"items": [], "pagination": {"limit": 10, "offset": 0, "total": 0}}
    inputs = {"response": MagicMock(json=lambda: response_data)}
    assert stream.next_page_token(**inputs) == {}


def test_parse_response_of_collection_items(patch_base_class):
    stream = CollectionContents()
    mock_record = {"id": "item-1", "isArchived": False, "isDraft": False, "fieldData": {"name": "item1_val"}}
    response_data = {"items": [mock_record]}
    inputs = {"response": MagicMock(json=lambda: response_data)}
    parsed_item = next(stream.parse_response(**inputs))
    assert parsed_item == mock_record


def test_collection_contents_path_uses_v2_live_items_endpoint(patch_base_class):
    stream = CollectionContents(collection_id="collection-1")
    assert stream.path() == "v2/collections/collection-1/items/live"


def test_get_json_schema_nests_fields_under_field_data(patch_base_class, mocker):
    mocker.patch.object(
        CollectionSchema,
        "read_records",
        return_value=iter([{"title": {"type": ["null", "string"]}}]),
    )
    stream = CollectionContents(collection_id="collection-1")
    schema = stream.get_json_schema()

    assert schema["properties"]["id"] == {"type": ["null", "string"]}
    assert schema["properties"]["isArchived"] == {"type": ["null", "boolean"]}
    field_data_schema = schema["properties"]["fieldData"]
    assert field_data_schema["type"] == ["null", "object"]
    assert field_data_schema["properties"]["title"] == {"type": ["null", "string"]}


def test_generate_streams(patch_base_class):
    SourceWebflow._get_collection_name_to_id_dict = MagicMock(return_value={"name-1": "id-1", "name-2": "id-2"})
    source = SourceWebflow()
    config_mock = MagicMock()
    streams = source.generate_streams(config_mock, "fake site id")
    assert len(list(streams)) == 2


def test_http_method(patch_base_class):
    stream = WebflowStream()
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = WebflowStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = WebflowStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
