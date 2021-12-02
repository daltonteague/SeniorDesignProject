#!/bin/sh
locust -f ./examples/iot_example.py --master --expect-slaves=2 --no-web -c 4 -r 1 --run-time 1m --host=http://google.com
