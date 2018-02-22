    -> Functionality "Evolve ALPACA CA one generation" is implemented by
    -> shell command
    -> "echo 'window={};' > ca.js && cat tests/appliances/yoob/playfield.js >> ca.js && ./bin/alpaca -c javascript %(test-body-file) >> ca.js && node ca.js"

