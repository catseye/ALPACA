"""
alpaca [-at] description.alp

Reference implementation of the ALPACA cellular automaton definition language,
version 1.0-PRE.

"""

from optparse import OptionParser
import sys

from alpaca import ast, scanner, parser, eval


def main(argv):
    optparser = OptionParser(__doc__.strip())
    optparser.add_option("-a", "--show-ast",
                         action="store_true", dest="show_ast", default=False,
                         help="show parsed AST instead of evaluating")
    optparser.add_option("-t", "--test",
                         action="store_true", dest="test", default=False,
                         help="run test cases and exit")
    (options, args) = optparser.parse_args(argv[1:])
    if options.test:
        import doctest
        (fails, something) = doctest.testmod()
        if fails == 0:
            print "All tests passed."
            sys.exit(0)
        else:
            sys.exit(1)
    file = open(args[0])
    text = file.read()
    file.close()
    p = parser.Parser(text)
    ast = p.alpaca()
    if options.show_ast:
        from pprint import pprint
        pprint(ast)
        sys.exit(0)
    sys.exit(0)
