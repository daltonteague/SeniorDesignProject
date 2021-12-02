"""
"""
import requests
import datetime
import sys
import re
import signal

from locust import events


class TestManager:
    """
    """

    def __init__(self, hostname, *args, **kwargs):
        """
        Creates and starts a TestManager that registers the test
        with the Nile Server and attaches itself to locust
        so that when locust closes it finalizes the test
        """
        self.hostname = hostname

        self.start_time = datetime.datetime.now().isoformat()

        slave_count = 0
        config_file = "locustfile.py"

        for i in range(len(sys.argv)):
            slave_arg = re.search(r"--expect-slaves=(\d+)", sys.argv[i])
            config_arg = re.search("^-f$", sys.argv[i]) \
                or re.search("^--locustfile$", sys.argv[i])
            if slave_arg:
                slave_count = slave_arg.group(1)
            if config_arg:
                config_file = sys.argv[i+1]
        
        self.arguments = ' '.join(sys.argv)
        print(self.arguments)
        self.config_file = config_file
        self.slave_count = slave_count

        if slave_count == 0:
            from .databuffer import DataBuffer
            DataBuffer(hostname, *args, **kwargs)

        self.start_test()
        
        events.quitting += self.finalize_test

    def start_test(self, **kwargs):
        print("Starting new test")
        data = {
          'config': self.arguments,
          'locustfile': self.config_file,
          'start': self.start_time,
          'workers': self.slave_count}

        start_endpoint = f'http://{self.hostname}/api/v1/tests'
        response = requests.post(start_endpoint, json=data)

        if response.status_code != 200:
            raise RuntimeError(f'Could not create test: \
                {response.status_code}')

        print("Nile: New Test Started")

    def finalize_test(self):
        print("Nile: Finalizing Test")

        self.end_time = datetime.datetime.now().isoformat()
        print(f"Nile: Test finalized with end time: {self.end_time}")
        data = {
          'end': self.end_time}
        finalize_endpoint = f'http://{self.hostname}/api/v1/tests/finalize'
        response = requests.post(finalize_endpoint, json=data)
        if response.status_code != 200:
            raise RuntimeError('Could not finalize test')
        else:
            print('Nile: Test Finalized')