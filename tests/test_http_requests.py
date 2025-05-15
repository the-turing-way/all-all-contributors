import pytest
import requests
import responses

from all_all_contributors.http_requests import get_request, patch_request, post_request

test_url = "http://jsonplaceholder.typicode.com/"
test_header = {"Authorization": "token ThIs_Is_A_ToKeN"}
test_body = {"Payload": "Send this with the request"}


@responses.activate
def test_get_request():
    responses.add(responses.GET, test_url, status=200)

    resp = get_request(test_url, headers=test_header)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == test_url
    assert resp.ok


@responses.activate
def test_get_request_json():
    responses.add(responses.GET, test_url, json={"Response": "OK"}, status=200)

    resp = get_request(test_url, headers=test_header, output="json")

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == test_url
    assert resp == {"Response": "OK"}


@responses.activate
def test_get_request_text():
    responses.add(responses.GET, test_url, json={"Response": "OK"}, status=200)

    resp = get_request(test_url, headers=test_header, output="text")

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == test_url
    assert resp == '{"Response": "OK"}'


def test_get_request_output_exception():
    with pytest.raises(ValueError):
        _ = get_request(test_url, headers=test_header, output="yaml")


@responses.activate
def test_get_request_url_exception():
    responses.add(responses.GET, test_url, status=500)

    with pytest.raises(requests.HTTPError):
        _ = get_request(test_url)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == test_url


@responses.activate
def test_post_request():
    responses.add(responses.POST, test_url, json={"Request": "Sent"}, status=200)

    post_request(test_url, headers=test_header, json=test_body)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == test_url
    assert responses.calls[0].response.text == '{"Request": "Sent"}'


@responses.activate
def test_post_request_return_json():
    responses.add(responses.POST, test_url, json={"Request": "Sent"}, status=200)

    resp = post_request(test_url, headers=test_header, json=test_body, return_json=True)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == test_url
    assert resp == {"Request": "Sent"}


@responses.activate
def test_post_request_exception():
    responses.add(
        responses.POST,
        test_url,
        status=500,
    )

    with pytest.raises(requests.HTTPError):
        post_request(test_url, headers=test_header, json=test_body)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == test_url


@responses.activate
def test_patch_request():
    responses.add(responses.PATCH, test_url, json={"Request": "Sent"}, status=200)

    patch_request(test_url, headers=test_header, json=test_body)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == test_url
    assert responses.calls[0].response.text == '{"Request": "Sent"}'


@responses.activate
def test_patch_request_return_json():
    responses.add(responses.PATCH, test_url, json={"Request": "Sent"}, status=200)

    resp = patch_request(
        test_url, headers=test_header, json=test_body, return_json=True
    )

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == test_url
    assert resp == {"Request": "Sent"}


@responses.activate
def test_patch_request_exception():
    responses.add(
        responses.PATCH,
        test_url,
        status=500,
    )

    with pytest.raises(requests.HTTPError):
        patch_request(test_url, headers=test_header, json=test_body)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == test_url
