#!/bin/bash

pytest -v tests/assn3_tests.py | tee assn3_test_results.txt
exit_code=$?
if [[ $exit_code != 0 ]]; then
  echo "tests failed" | tee -a /tmp/log.txt  # TODO: this never happens!
else
  echo "tests succeeded" | tee -a /tmp/log.txt
fi