    -> Functionality "Evolve ALPACA CA one generation" is implemented by
    -> shell command
    -> "cat tests/appliances/nodejs/prelude.js tests/appliances/yoob/playfield.js > ca.js && ./bin/alpaca -c javascript %(test-body-file) >> ca.js && cat tests/appliances/nodejs/postlude.js >> ca.js && node ca.js"

