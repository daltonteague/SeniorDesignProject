#!/bin/sh
locust -f ./examples/iot_example.py --slave --master-host=localhost
