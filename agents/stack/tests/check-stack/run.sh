#!/bin/bash
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
stack=$(cd "$here/../.." && pwd)
python3 "$here/fixtures.py" "$stack/bin/check-stack"
