"""Various assertion methods for use in testing."""

from typing import Any

from requests import Response


def response_code(response: Response, status_code: int = 200):
    """Ensure that the provided response returned a status code."""
    assert response.status_code == status_code, f"{response.url} must return {status_code}"


def redirect(response: Response, expected: str):
    """Ensure that the provided response was a redirect to the expected location."""
    assert response.history, f"Expected a redirect from {response.url}, but one was not provided."
    assert expected in response.url, f"Expected a redirect to {expected}."


def maximum_redirects(response: Response, maximum: int):
    """Ensure that the provided response did not exceed the maximum redirects."""
    redirects = len(response.history)
    assert maximum <= redirects, f"Exceeded maximum number of redirects ({redirects}/{maximum})"


def has_header(response: Response, header: str):
    """Ensure that the response contains the provided header."""
    assert header in response.headers, f"Response does not contain header '{header}'"


def header_equals(response: Response, header: str, value: Any):
    """Ensure that the respones contains the header with specified value."""
    has_header(response, header)
    assert response.headers[header] == value, f"Response headers do not contain {header}={value}."


def response_contains(response: Response, content: str):
    """Ensure that the response contains the specified content."""
    assert content in response.text, f"Response content does not contain '{content}'"


def response_not_contains(response: Response, content: str):
    """Ensure that the response does not contain the specified content."""
    assert content not in response.text, f"Response content should not contain '{content}'"
