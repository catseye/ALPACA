#!/bin/sh

cat >test_config <<EOF
    -> Functionality "Parse ALPACA Description" is implemented by shell command
    -> "./bin/alpaca -p %(test-file) && echo 'ok'"
EOF
falderal test_config doc/ALPACA.markdown
rm test_config
