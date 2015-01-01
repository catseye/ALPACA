#!/bin/sh

# usage: ./test.sh [js]
# js option will test compiling to Javascript (requires node.js.)

bin/alpaca -t || exit 1

cat >test_config <<EOF
    -> Functionality "Parse ALPACA Description" is implemented by shell command
    -> "./bin/alpaca -p %(test-body-file) && echo 'ok'"

    -> Functionality "Evolve ALPACA CA one generation" is implemented by
    -> shell command
    -> "./bin/alpaca -I -g1 %(test-body-file)"
EOF

if [ "x$1" = "xjs" ]; then
    cat >>test_config <<EOF

    -> Functionality "Evolve ALPACA CA one generation" is implemented by
    -> shell command
    -> "./bin/alpaca -y -c javascript %(test-body-file) > ca.js && node ca.js"
EOF
fi

falderal test_config doc/ALPACA.markdown
EXITCODE=$?
rm test_config
exit $EXITCODE
