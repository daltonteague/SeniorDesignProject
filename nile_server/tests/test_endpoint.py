import unittest

from app import app, db
from app.models import Test, Request, SystemMetric
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

import datetime
import time
import requests
import json

#########################
# Fields Setup #
#########################

api = 'http://localhost:5000/api/v1'
test_endpoint = f'{api}/tests'
met_endpoint = f'{api}/metrics'
req_endpoint = f'{api}/requests'

test_file = "locustfile"
test_config = "Test POST Config"
num_workers = 50000

req_name = "Test Request"
req_method = "POST"
req_length = 200
res_type = "response type"
res_length = 300
res_time = 500
status = "200"
success = True

sys_name = "Test System"
met_name = "Test Metric"
met_val = 150


class TestEndpoint(unittest.TestCase):

    """
    These tests cover possible endpoint requests and
    the server's handling of those requests. This includes
    creating new tests, adding requests and metrics to them,
    and finalizing them.
    """

    #########################
    # Test Environment Setup #
    #########################

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()

    #########################
    # Test POST section #
    #########################

    def test_00_no_tests(self):

        """
        Test adding requests, metrics and test end time when no test running,
        expected to fail
         """

        # In case a previous test is still open for some reason
        finalize_test()
        reset_db()

        self.assertEqual(Test.query.count(), 0)
        self.assertEqual(Request.query.count(), 0)
        self.assertEqual(SystemMetric.query.count(), 0)

        print("Testing empty database")

        request = add_request()
        self.assertEqual(
            request.text,
            "Can't submit request while no tests running."
            )
        self.assertEqual(request.status_code, 400)

        request = add_metric()
        self.assertEqual(
            request.text,
            "Can't submit metric while no tests running."
            )
        self.assertEqual(request.status_code, 400)

        request = finalize_test()
        self.assertEqual(
            request.text,
            "No test running."
            )

    def test_01_post_test(self):

        """ Test adding new test """

        print("Testing post test")

        count = Test.query.count()

        request = add_test()

        self.assertEqual(Test.query.count(), count + 1)
        self.assertIn(
            'Added test with ID:',
            request.text
            )

    def test_02_post_request(self):

        """ Test adding new request """

        print("Testing post requests")

        count = Request.query.count()

        request = add_request(5)
        time.sleep(4)
        self.assertEqual(Request.query.count(), count + 5)
        self.assertIn(
            'Added request with ID: ',
            request.text
            )

    def test_03_post_metric(self):

        """ Test adding new metric """

        print("Testing post metric")

        count = SystemMetric.query.count()

        request = add_metric()

        self.assertIn(
            'Added metric with ID:',
            request.text
            )
        self.assertEqual(SystemMetric.query.count(), count + 1)

    def test_04_post_finalize(self):

        """
        Here we test that we can save requests even if they aren't
        posted until after their running test has been finalized
        """

        print("Testing finalize test request")

        req_time = now()
        time.sleep(1)
        test_end = now()

        request = finalize_test(test_end)
        self.assertIn("Finalized test with ID:", request.text)

        self.assertEqual(
            db.session.query(Test)
            .order_by(Test.id.desc()).first().end.isoformat(),
            test_end
            )

        request = add_request(1, req_time)
        self.assertIn(
            'Added request with ID: ',
            request.text
            )

        # If request doesn't fall within the Test time period,
        # it cannot be added
        request = add_request(1)
        self.assertEqual(
            request.text,
            "Can't submit request while no tests running."
            )
        self.assertEqual(request.status_code, 400)

    def test_05_post_invalid(self):

        """ Test posting invalid data, expected to fail """

        print("Testing invalid post requests")

        # Add invalid test
        request = add_test('5:35 PM')
        self.assertEqual(request.status_code, 500)

        # Add valid test to test invalid metrics and requests
        request = add_test()
        self.assertEqual(request.status_code, 200)

        # Attempt to add test while a test is running
        request = add_test()
        self.assertEqual(request.text, 'Can only run one test at a time.')

        request = add_metric('5 o clock')
        self.assertEqual(request.status_code, 400)

        request = add_request(1, 'Tea time')
        self.assertEqual(request.status_code, 500)

        # Fail to finalize test
        request = finalize_test('Late at night')
        self.assertEqual(request.status_code, 500)

        # Finalize test
        request = finalize_test()
        self.assertIn("Finalized test with ID:", request.text)

        # Fail to add request and metric after test is finished
        request = add_request(1)
        self.assertIn(
            "Can't submit request while no tests running.",
            request.text
            )

        request = add_metric()
        self.assertIn(
            "Can't submit metric while no tests running.",
            request.text
            )

    def test_06_delete(self):

        """ Test adding a test with test data and deleting all of it """

        print("Testing deletion of test data")

        request = add_test()
        self.assertEqual(request.status_code, 200)

        request = add_request(5)
        self.assertEqual(request.status_code, 200)

        request = add_metric()
        self.assertEqual(request.status_code, 200)

        request = finalize_test()
        self.assertEqual(request.status_code, 200)

        test_count = Test.query.count()
        req_count = Request.query.count()
        met_count = SystemMetric .query.count()

        id = db.session.query(
            Test
            ).order_by(
                Test.id.desc()
            ).first().id

        endpoint = f'{api}/delete/{id}'
        request = requests.post(endpoint)

        self.assertEqual(
            request.text,
            f"Deleted test and data with ID: {id}\n"
            )
        self.assertEqual(request.status_code, 200)

        self.assertEqual(Test.query.count(), test_count - 1)
        self.assertEqual(Request.query.count(), req_count - 5)
        self.assertEqual(SystemMetric.query.count(), met_count - 1)

    #########################
    # Test GET section #
    #########################

    def test_07_get_all(self):

        """ Test getting a list of all test, request and metrics """

        print("Testing get all tests")

        endpoint = test_endpoint
        tests = json.loads(requests.get(endpoint).content)

        self.assertEqual(len(tests), Test.query.count())

        print("Testing get all requests")

        endpoint = req_endpoint
        loc_requests = json.loads(requests.get(endpoint).content)

        self.assertEqual(len(loc_requests), Request.query.count())

        print("Testing get all metrics")

        endpoint = met_endpoint
        metrics = json.loads(requests.get(endpoint).content)

        self.assertEqual(len(metrics), SystemMetric.query.count())

    def test_08_get_request_id(self):

        """ Test receiving requests by id """

        print('Testing get request by id')

        add_request()

        request_id = db.session.query(
            Request
            ).order_by(
                Request.id.desc()
            ).first().id

        endpoint = f'{req_endpoint}/{request_id}'
        request = json.loads(requests.get(endpoint).content)

        # Check fields match what is expected

        self.assertEqual(request['name'], req_name)
        self.assertEqual(request['request_method'], req_method)
        self.assertEqual(request['request_length'], req_length)
        self.assertEqual(request['response_length'], res_length)
        self.assertEqual(request['response_time'], res_time)
        self.assertEqual(request['status_code'], status)
        self.assertEqual(request['success'], success)
        self.assertEqual(request['exception'], None)

        # Test getting the request through its test's id
        test_id = request['test_id']

        endpoint = f'{req_endpoint}/test/{test_id}'
        request = json.loads(requests.get(endpoint).content)

        # Check fields match what is expected
        num_requests = Request.query.filter(
            Request.test_id == test_id
        ).count()

        self.assertTrue(len(request['timestamps']) == num_requests)

        requests.get(f'http://localhost:5000/tests/{test_id}')

    def test_09_get_metric_id(self):

        """ Test receiving metrics by id """

        print('Testing get metric by id')

        metric_id = db.session.query(
            SystemMetric
            ).order_by(
                SystemMetric.id.desc()
            ).first().id

        endpoint = f'{met_endpoint}/{metric_id}'
        request = json.loads(requests.get(endpoint).content)

        self.assertEqual(request['system_name'], sys_name)
        self.assertEqual(request['metric_name'], met_name)
        self.assertEqual(request['metric_value'], met_val)

    def test_10_get_test_id(self):

        """ Test tests requests by id """

        print('Testing get test by id')

        test_id = db.session.query(Test).order_by(Test.id.desc()).first().id

        endpoint = f'{test_endpoint}/{str(test_id)}'
        request = json.loads(requests.get(endpoint).content)

        self.assertEqual(request['workers'], num_workers)

    def test_11_end(self):

        """ Up the coverage report for rendering web
            pages for which selenium tests have not yet
            been implemented.
        """

        test_id = db.session.query(Test).order_by(Test.id.desc()).first().id

        requests.get('http://localhost:5000/index')
        requests.get('http://localhost:5000/graphs')
        requests.get(f'http://localhost:5000/tests/{test_id}')

        reset_db()


#########################
# Helper functions  #
#########################


def add_test(time=None):

    """
    Helper for making a test post

    Arguments
        * time - can specify a timestamp for test being added
    """

    endpoint = test_endpoint

    data = {
        'config': (test_config),
        'locustfile': test_file,
        'start': time if time else now(),
        'workers': num_workers
    }

    return requests.post(endpoint, json=data)


def add_request(count=1, time=None):

    """
    Helper for making a request post

    Arguments
        * count - can add any number of requests at once
        * time - can specify a timestamp for request being added
    """

    request_list = []
    endpoint = req_endpoint

    while count > 0:
        data = {
            'name': req_name,
            'request_timestamp': time if time else now(),
            'request_method': req_method,
            'request_length': req_length,
            'response_length': res_length,
            'response_time': res_time,
            'status_code': status,
            'success': success,
            'exception': None
        }

        request_list.append(data)
        count -= 1

    return requests.post(endpoint, json=request_list)


def add_metric(time=None):

    """
    Helper for making a metric post

    Arguments
        * time - can specify a timestamp for metric being added
    """

    endpoint = met_endpoint

    data = {
        'system_name': sys_name,
        'metric_name': met_name,
        'metric_timestamp':  time if time else now(),
        'metric_value': met_val,
    }
    return requests.post(endpoint, json=data)


def finalize_test(time=None):

    """
    Helper for finalizing a test

    Arguments
        * time - can specify the test's end time
    """

    endpoint = f"{test_endpoint}/finalize"

    data = {
        'end': time if time else now()
    }

    return requests.post(endpoint, json=data)


def now():

    """ Shorthand function for getting formatted date """

    return datetime.datetime.now().isoformat()


def reset_db():

    """ Clears the database for the next test"""

    print('Resetting database...')
    print(f'Tests: {Test.query.count()}')
    print(f'Requests: {Request.query.count()}')
    print(f'Metrics: {SystemMetric.query.count()}')

    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(f'Clearing table {table}')
        db.session.execute(table.delete())
        print(f'Cleared table {table}')

    db.session.commit()

    print(f'Tests: {Test.query.count()}')
    print(f'Requests: {Request.query.count()}')
    print(f'Metrics: {SystemMetric.query.count()}')


if __name__ == '__main__':
    unittest.main()
