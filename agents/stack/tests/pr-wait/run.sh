#!/bin/sh
set -eu
unset PYTHONOPTIMIZE

test_dir=$(CDPATH='' cd "$(dirname "$0")" && pwd)
exec python3 "$test_dir/test_pr_wait.py"
