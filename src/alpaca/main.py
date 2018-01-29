"""
alpaca [-afgIJpt] [-c backend] [-d string] description.alp [form.ca]

Reference implementation of the ALPACA cellular automaton definition language,
version 1.0.

"""

from argparse import ArgumentParser
import sys

from alpaca import analysis
from alpaca.analysis import (
    construct_representation_map,
    get_default_state,
    get_defined_playfield,
)
from alpaca.eval import evolve_playfield
from alpaca.parser import Parser
from alpaca.playfield import Playfield


def main(argv):
    argparser = ArgumentParser()

    argparser.add_argument('source', metavar='SOURCE', type=str,
        help='Name of the file containing the ALPACA description to process, '
             'or "test" to run internal tests only and exit'
    )

    argparser.add_argument("-a", "--show-ast", action="store_true",
        help="show parsed AST instead of evaluating"
    )
    argparser.add_argument("-c", "--compile-to", metavar='BACKEND', default=None,
        help="compile to given backend code instead "
             "of evaluating directly (available backends: javascript)"
    )
    argparser.add_argument("-d", "--divider", metavar='STRING',
        default="-----",
        help="set the string shown between generations "
             "(default: '-----')"
    )
    argparser.add_argument("-f", "--halt-at-fixpoint", action="store_true",
        help="stop evolving CA when it comes to a trivial "
             "fixed point (playfield = previous playfield)"
    )
    argparser.add_argument("-g", "--generations", metavar='COUNT',
                         dest="generations", default=None, type=int,
                         help="evolve CA for only the given number of "
                              "generations")
    argparser.add_argument("-I", "--hide-initial", action="store_false", dest="show_initial",
        help="don't show initial configuration"
    )
    argparser.add_argument("-J", "--hide-intermediate",
                         action="store_false", dest="show_intermediate",
                         default=True,
                         help="don't show intermediate configurations "
                              "(only show final configuration)")
    argparser.add_argument("-p", "--parse-only", action="store_true",
        help="parse the ALPACA description only and exit"
    )
    argparser.add_argument("-v", "--verbose", action="store_true",
        help="run verbosely"
    )
    argparser.add_argument("-y", "--include-yoob-playfield-inline", action="store_true",
        help="include yoob/playfield.js (from yoob.js) "
             "inline in generated Javascript (javascript "
             "backend only)"
    )

    options = argparser.parse_args(argv[1:])

    if options.source == 'test':
        import doctest
        (fails, something) = doctest.testmod(analysis)
        if fails == 0:
            print "All tests passed."
            sys.exit(0)
        else:
            sys.exit(1)

    with open(options.source, 'r') as f:
        text = f.read()

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

    def begin_output():
        # TODO if not dumping to seperate files, then
        print_divider()

    def output_frame(count, pf):
        # TODO if not dumping to seperate files, then
        print str(pf),
        print_divider()

    count = 0
    begin_output()
    if options.show_initial:
        output_frame(count, pf)
    while True:
        new_pf = Playfield(default_state, repr_map)
        evolve_playfield(pf, new_pf, ast, verbose=options.verbose)
        new_pf.recalculate_limits()
        if options.halt_at_fixpoint:
            if pf.equals(new_pf):
                break
        pf = new_pf
        count += 1
        if (options.show_intermediate or
            (options.generations is not None and
             count == options.generations - 1)):
            output_frame(count, pf)
        if (options.generations is not None and
            count >= options.generations):
            break

    sys.exit(0)
