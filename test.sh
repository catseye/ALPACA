#!/bin/sh

# usage: ./test.sh
# If node (node.js) is on path, will also test compiling to Javascript.

bin/alpaca test -v || exit 1

APPLIANCES="tests/appliances/alpaca.md"
if [ x`which nodejs` != "x" ]; then
    APPLIANCES="$APPLIANCES tests/appliances/nodejs.md"
fi

falderal $APPLIANCES doc/ALPACA.markdown
EXITCODE=$?
rm -f ca.js
exit $EXITCODE
