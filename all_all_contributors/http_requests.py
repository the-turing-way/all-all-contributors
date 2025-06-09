"""
A set of basic functional wrappers around HTTP verbs

- get: customise response format
- patch
- post
"""

import requests


def get_request(url, headers={}, params={}, output="default"):
    """Send a GET request to an HTTP API endpoint

    Args:
        url (str): The URL to send the request to
        headers (dict, optional): A dictionary of headers to send with the
            request. Defaults to an empty dict.
        params (dict, optional): A dictionary of parameters to send with the
            request. Defaults to an empty dict.
        output (str): The format in which to output the response in. Currently
            accepts 'default', 'json' or 'text'. 'default' does not apply any
            format parsing of the response.

    Returns:
        resp: A formatted response from the HTTP request

    Raises:
        ValueError: An unexpected output format was chosen.
    """
    accepted_formats = ["default", "json", "text"]
    if output not in accepted_formats:
        raise ValueError(
            "Invalid output format. Please choose one of the following options: %s"
            % accepted_formats
        )

    resp = requests.get(url, headers=headers, params=params)

    if not resp:
        raise requests.HTTPError(f"{resp.text}\nRequest URL: {url}")

    if output == "default":
        return resp
    elif output == "json":
        return resp.json()
    elif output == "text":
        return resp.text


def patch_request(url, headers={}, json={}, return_json=False):
    """Send a PATCH request to an HTTP API endpoint

    Args:
        url (str): The URL to send the request to
        headers (dict, optional): A dictionary of any headers to send with the
            request. Defaults to an empty dictionary.
        json (dict, optional): A dictionary containing JSON payload to send with
            the request. Defaults to an empty dictionary.
        return_json (bool, optional): Return the JSON payload response.
            Defaults to False.

    Returns:
        resp: A JSON formatted response from a HTTP response

    Raises:
        HTTPError: An error was returned by the HTTP request
    """
    resp = requests.patch(url, headers=headers, json=json)

    if not resp:
        raise requests.HTTPError(f"{resp.text}\nRequest URL: {url}")

    if return_json:
        return resp.json()


def post_request(url, headers={}, json={}, return_json=False):
    """Send a POST request to an HTTP API endpoint

    Args:
        url (str): The URL to send the request to
        headers (dict, optional): A dictionary of any headers to send with the
            request. Defaults to an empty dictionary.
        json (dict, optional): A dictionary containing JSON payload to send with
            the request. Defaults to an empty dictionary.
        return_json (bool, optional): Return the JSON payload response.
            Defaults to False.

    Returns:
        resp: A JSON formatted response from a HTTP request

    Raises:
        HTTPError: An error was returned by the HTTP request
    """
    resp = requests.post(url, headers=headers, json=json)

    if not resp:
        raise requests.HTTPError(f"{resp.text}\nRequest URL: {url}")

    if return_json:
        return resp.json()
