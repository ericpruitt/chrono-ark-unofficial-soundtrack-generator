#!/bin/sh
set -e -u -f
trap 'rm -f README.md.tmp' EXIT

{
    sed -n  '1,/Track List:/p' README.md
    echo
    awk -F \" '/"name":/ { printf "%d. %s\n", ++x, $4 }' make.py
} > README.md.tmp

diff_status=0
diff -u README.md README.md.tmp || diff_status="$?"

if [ "$diff_status" -eq 1 ]; then
    mv README.md.tmp README.md
elif [ "$diff_status" -ne 0 ]; then
    exit "$diff_status"
fi
