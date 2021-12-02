from locust import events
from nile_test.dataflow.http_client import HTTPClient


def test_init():
    """
    Tests that the defaults dict contains the correct values when an
    HTTPClient is constructed
    """
    sink = HTTPClient(method="post", url="http://localhost:8000")
    assert sink.defaults == {"method": "post", "url": "http://localhost:8000"}


def test_write(echo_server):
    """
    Tests that the HTTPClient sends requests to a server correctly

    This test uses the echo_server fixture, see conftest.py for more details
    """
    sink = HTTPClient(url="http://localhost:8000")

    # Setup event hooks and variables to detect when requests
    # With certain types are sent
    delete_found = False
    post_found = False
    get_found = False

    def catch_delete(request_type, **kwargs):
        nonlocal delete_found
        if request_type == "DELETE":
            delete_found = True

    def catch_post(request_type, **kwargs):
        nonlocal post_found
        if request_type == "POST":
            post_found = True

    def catch_get(request_type, **kwargs):
        nonlocal get_found
        if request_type == "GET":
            get_found = True

    events.request_success += catch_delete
    events.request_success += catch_post
    events.request_success += catch_get

    # Send each request, verifying that the correct types
    # have been found after each step
    assert not delete_found and not post_found and not get_found

    sink.write([{"method": "DELETE"}])
    assert delete_found and not post_found and not get_found

    sink.write([{"method": "POST", "data": "2"}])
    assert delete_found and post_found and not get_found

    sink.write([{"method": "GET"}])
    assert delete_found and post_found and get_found
