from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config
from app import app, db
from app.models import Test, Request, SystemMetric

import os
import datetime
import time
import random

# App config setup
app.config.from_object(os.environ['APP_CONFIG_ENV'])

# Flask migration setup
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


# Start the server and run test suite
@manager.command
def test():
    """
    Run the tests within tests/test_endpoint and run
    the test server in parallel to produce a coverage report.
    """

    test_command = ['nose2', 'tests.test_endpoint']

    # Set the test environment
    os.putenv("APP_CONFIG_ENV", "config.TestConfig")
    app.config.from_object(os.environ['APP_CONFIG_ENV'])

    return start_test_server(test_command)


def start_test_server(test):
    import subprocess
    import requests

    # Start the server in a subprocess with coverage
    coverage_prefix = ["coverage", "run", "-m", "--source", "."]
    server_command = coverage_prefix + ["webservice"]
    server = subprocess.Popen(server_command, stderr=subprocess.PIPE)
    time.sleep(3)
    # Assert the server has started before continuing
    for line in server.stderr:
        if line.startswith(b' * Running on'):
            break

    # Run the tests in another subprocess
    test_process = subprocess.Popen(test)
    test_process.wait(timeout=60)

    # Once tests have run, shutdown the server
    shutdown_url = 'http://localhost:5000/shutdown'
    requests.post(shutdown_url)
    server_return_code = server.wait(timeout=60)

    # Display the coverage report for the server
    os.system("coverage report -i webservice.py")

    # Reset the environment variable
    os.putenv("APP_CONFIG_ENV", "config.DevelopmentConfig")
    app.config.from_object(os.environ['APP_CONFIG_ENV'])
    print('Tests finished!')

    return server_return_code


@manager.command
def seed(num_tests=10, reqs_per_test=100):
    """
    Seed the test database with data by adding a test with
    a large number of requests

    Arguments
        * num_tests - number of tests to insert
        * reqs_per_test - number of requests to insert per test
    """

    if os.environ['APP_CONFIG_ENV'] != 'config.TestConfig':
        print(
            'You can only seed the test database.',
            'Set APP_CONFIG_ENV environment variable to config.TestConfig',
            'and try again.'
        )
        return

    test_count = 0
    req_count = 0

    while test_count < int(num_tests):
        print(f'Adding test {test_count + 1} with {reqs_per_test} requests')
        new_test = Test(
            config=f"Seed {Test.query.count()}",
            locustfile="locustfile.py",
            start=now(),
            end=now(),
            workers=5000
        )
        db.session.add(new_test)
        db.session.commit()
        test_id = new_test.id

        reqs = []
        while req_count < int(reqs_per_test):

            new_request = Request(
                test_id=test_id,
                name=f"Seed {req_count}",
                request_timestamp=now(),
                request_method="Request Method",
                request_length=250,
                response_length=250,
                response_time=random.normalvariate(240, 1),
                status_code=200,
                success=True,
                exception=None
            )
            reqs.append(new_request)
            req_count += 1
            time.sleep(.001)

        db.session.bulk_save_objects(reqs)
        db.session.commit()

        req_count = 0
        test_count += 1

    print('Finished seeding database')


def now():

    """ Shorthand method for getting formatted date """

    return datetime.datetime.now().isoformat()


if __name__ == '__main__':
    manager.run()
