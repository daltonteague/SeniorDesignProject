import time
from requests import request, HTTPError
from collections import ChainMap
from interface import implements


from locust import events

from . import Sink


class HTTPClient(implements(Sink)):
    """
    An HTTPClient is a Sink that sends data
    written to it to the specified server
    """

    def __init__(self, **defaults):
        """
        Creates an HTTPClient

        Arguments:
         The keyword arguments provided act as duplicates for the fields
         read from records written to this client.
         For more info see HTTPClient.write()
        """
        self.defaults = defaults

    def write(self, records):
        """
        Sends records to an HTTP server

        Each record that is not a dictionary is ignored.
        Each dictionary record is overlayed onto the defaults
        provided to the client.

        The following fields must be defined in
        either the record or the overlay.
         * method - the HTTP method to use
         * url - the URL to send to

        The following additional fields may also be provided
         * params - a dictionary of query string parameters
         * data - data to be sent in the body of the request
         * headers - a dictionary of HTTP headers
        """
        for record in records:
            self._write_one(record)

    def _write_one(self, record):
        optionals = {
            "params": {},
            "data": {},
            "headers": {}
        }
        record = ChainMap(record, self.defaults, optionals)

        if "method" not in record:
            raise ValueError("Must provide 'method'")

        if "url" not in record:
            raise ValueError("Must provide 'url'")

        time_sent = time.time()

        response = request(record["method"], record["url"],
                           params=record["params"], data=record["data"],
                           headers=record["headers"])

        response_time = time.time() - time_sent

        if response.ok:
            events.request_success.fire(
                request_type=record["method"],
                name=record["url"],
                response_time=response_time,
                response_length=len(response.content),
            )
        else:
            try:
                response.raise_for_status()

                events.request_failure.fire(
                    request_type=record["method"],
                    name=record["url"],
                    response_time=response_time,
                    response_length=len(response.content),
                    exception=RuntimeError(
                        f"Request failed with {response.content}")
                )
            except HTTPError as error:
                events.request_failure.fire(
                    request_type=record["method"],
                    name=record["url"],
                    response_time=response_time,
                    response_length=len(response.content),
                    exception=error
                )
