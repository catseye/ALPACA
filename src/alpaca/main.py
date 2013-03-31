"""
alpaca [-afgIJpt] [-c backend] [-d string] description.alp [form.ca]

Reference implementation of the ALPACA cellular automaton definition language,
version 1.0.

"""

from optparse import OptionParser
import sys

from alpaca.analysis import (
    construct_representation_map,
    get_default_state,
    get_defined_playfield,
)
from alpaca.eval import evolve_playfield
from alpaca.parser import Parser
from alpaca.playfield import Playfield


def main(argv):
    optparser = OptionParser(__doc__.strip())
    optparser.add_option("-a", "--show-ast",
                         action="store_true", dest="show_ast", default=False,
                         help="show parsed AST instead of evaluating")
    optparser.add_option("-c", "--compile-to", metavar='BACKEND',
                         dest="compile_to", default=None,
                         help="compile to given backend code instead "
                              "of evaluating directly (available backends: "
                              "javascript)")
    optparser.add_option("-d", "--divider", metavar='STRING',
                         dest="divider", default="-----",
                         help="set the string shown between generations "
                              "(default: '-----')")
    optparser.add_option("-f", "--halt-at-fixpoint",
                         action="store_true", dest="halt_at_fixpoint",
                         default=False,
                         help="stop evolving CA when it comes to a trivial "
                              "fixed point (playfield = previous playfield)")
    optparser.add_option("-g", "--generations", metavar='COUNT',
                         dest="generations", default=None, type='int',
                         help="evolve CA for only the given number of "
                              "generations")
    optparser.add_option("-I", "--hide-initial",
                         action="store_false", dest="show_initial",
                         default=True,
                         help="don't show initial configuration")
    optparser.add_option("-J", "--hide-intermediate",
                         action="store_false", dest="show_intermediate",
                         default=True,
                         help="don't show intermediate configurations "
                              "(only show final configuration)")
    optparser.add_option("-p", "--parse-only",
                         action="store_true", dest="parse_only",
                         default=False,
                         help="parse the ALPACA description only and exit")
    optparser.add_option("-t", "--test",
                         action="store_true", dest="test", default=False,
                         help="run test cases and exit")
    optparser.add_option("-y", "--include-yoob-playfield-inline",
                         action="store_true",
                         dest="include_yoob_playfield_inline", default=False,
                         help="include yoob/playfield.js (from yoob.js) "
                              "inline in generated Javascript (javascript "
                              "backend only)")
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
    if options.parse_only:
        sys.exit(0)
    if options.show_ast:
        from pprint import pprint
        pprint(ast)
        sys.exit(0)

    default_state = get_default_state(ast)
    repr_map = construct_representation_map(ast)

    if options.compile_to is not None:
        # XXX generalize
        if options.compile_to == 'javascript':
            from alpaca.backends.javascript import Compiler
            compiler = Compiler(ast, sys.stdout, options=options)
            success = compiler.compile()
            if success:
                sys.exit(0)
        else:
            print "unsupported backend '%s'" % options.compile_to
        sys.exit(1)

    pf = get_defined_playfield(ast)
    if pf is None:
        if len(args) < 2:
            print "source file does not define an initial configuration,"
            print "and no cellular automaton configuration file given"
            sys.exit(1)
        file = open(args[1])
        pf = Playfield(default_state, repr_map)
        pf.load(file)
        file.close()

    def print_divider():
        # TODO: allow formatting string in the divider, esp.
        # to show the # of this generation
        if options.divider != '':
            print options.divider

    count = 0
    print_divider()
    if options.show_initial:
        print str(pf),
        print_divider()
    while True:
        new_pf = Playfield(default_state, repr_map)
        evolve_playfield(pf, new_pf, ast)
        new_pf.recalculate_limits()
        if options.halt_at_fixpoint:
            if pf.equals(new_pf):
                break
        pf = new_pf
        if (options.show_intermediate or
            (options.generations is not None and
             count == options.generations - 1)):
            print str(pf),
            print_divider()
        count += 1
        if (options.generations is not None and
            count >= options.generations):
            break

    sys.exit(0)
