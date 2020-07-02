#!/bin/sh -l

echo "HOSTNAME=$1"
echo "VERIFY_SSL=$2"

cd $HOME
HOSTNAME=$1 VERIFY_SSL=$2 pytest /src/tests.py
exit $?
