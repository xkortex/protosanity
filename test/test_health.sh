#!/usr/bin/env bash

# pip install . before running this script
python -m foolib.server &
PID_SERVER=$!

sleep 0.1
python -m foolib.client --health
python -m foolib.client --health
kill $PID_SERVER

