    -> Functionality "Parse ALPACA Description" is implemented by shell command
    -> "./bin/alpaca -p %(test-body-file) && echo 'ok'"

    -> Functionality "Evolve ALPACA CA one generation" is implemented by
    -> shell command
    -> "./bin/alpaca -I -g1 %(test-body-file)"

    -> Functionality "Parse ALPACA Description" is implemented by shell command
    -> "python3 ./bin/alpaca -p %(test-body-file) && echo 'ok'"

    -> Functionality "Evolve ALPACA CA one generation" is implemented by
    -> shell command
    -> "python3 ./bin/alpaca -I -g1 %(test-body-file)"
