#!/bin/sh -l

echo "HOSTNAME=$1"
echo "VERIFY_SSL=$2"

HOSTNAME=$1 VERIFY_SSL=$2 pytest src/tests.py

echo "Hello $1"
time=$(date)
echo "::set-output name=time::$time"