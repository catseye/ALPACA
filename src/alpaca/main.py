"""
alpaca [-agt] description.alp [form.ca]

Reference implementation of the ALPACA cellular automaton definition language,
version 1.0-PRE.

"""

from optparse import OptionParser
import sys

from alpaca.eval import evolve_playfield
from alpaca.parser import Parser
from alpaca.playfield import Playfield


def main(argv):
    optparser = OptionParser(__doc__.strip())
    optparser.add_option("-a", "--show-ast",
                         action="store_true", dest="show_ast", default=False,
                         help="show parsed AST instead of evaluating")
    optparser.add_option("-g", "--generations",
                         dest="generations", default=None, type='int',
                         help="evolve CA for only the given number of "
                              "generations")
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
    ast = Parser(text).alpaca()
    if options.show_ast:
        from pprint import pprint
        pprint(ast)
        sys.exit(0)

    # XXX if has_own_defined_playfield(ast): pf = get_playfield_from(ast): else...
    file = open(args[1])
    map = {'*': 'Alive', ' ': 'Dead'}
    pf = Playfield('Dead', map)
    pf.load(file)
    file.close()

    count = 0
    print str(pf)
    print "-----"
    while True:
        new_pf = Playfield('Dead', map)
        evolve_playfield(pf, new_pf, ast)
        new_pf.recalculate_limits()
        pf = new_pf
        print str(pf),
        print "-----"
        count += 1
        if (options.generations is not None and
            count >= options.generations):
            break
            
    sys.exit(0)
