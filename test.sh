#!/bin/sh

# usage: ./test.sh
# If node (node.js) is on path, will also test compiling to Javascript.

bin/alpaca -t || exit 1

cat >test_config <<EOF
    -> Functionality "Parse ALPACA Description" is implemented by shell command
    -> "./bin/alpaca -p %(test-body-file) && echo 'ok'"

    -> Functionality "Evolve ALPACA CA one generation" is implemented by
    -> shell command
    -> "./bin/alpaca -I -g1 %(test-body-file)"
EOF

if [ x`which node` != "x" ]; then
    cat >>test_config <<EOF

    -> Functionality "Evolve ALPACA CA one generation" is implemented by
    -> shell command
    -> "./bin/alpaca -y -c javascript %(test-body-file) > ca.js && node ca.js"
EOF
fi

falderal test_config doc/ALPACA.markdown
EXITCODE=$?
rm -f test_config ca.js
exit $EXITCODE
