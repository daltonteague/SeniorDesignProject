#!/bin/sh
locust -f ./examples/locust_file.py --slave --master-host=localhost
