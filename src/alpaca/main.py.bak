"""
alpaca [-afgIJpt] [-c backend] [-d string] description.alp [form.ca]

Reference implementation of the ALPACA cellular automaton definition language,
version 1.0.

"""

from argparse import ArgumentParser
import os
import re
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
    argparser.add_argument("-i", "--initial-configuration", metavar='FILENAME',
        type=str, default=None, help="initial configuration to load into playfield "
                                     "(when evolving a playfield only)"
    )
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

    argparser.add_argument("--display-window", metavar='RANGE', default=None,
        help="A string in the form '(x1,y1)-(x2-y2)'; if given, every generation "
             "displayed will only display the cells within this fixed window"
    )
    argparser.add_argument("--display-svg", action="store_true",
        help="Display each generation as SVG"
    )
    argparser.add_argument("--stylesheet", metavar='FILENAME', default=None,
        help="Use the given file as the ALPACA stylesheet "
             "(only supported in SVG output currently)"
    )
    argparser.add_argument("--write-discrete-files-to", metavar='DIRNAME', default=None,
        help="If given, instead of displaying each generation on standard output, "
             "write it to a new numbered file in this directory"
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

    display_x1, display_y1, display_x2, display_y2 = None, None, None, None
    if options.display_window:
        match = re.match(r'^\((-?\d+)\,(-?\d+)\)\-\((-?\d+)\,(-?\d+)\)$', options.display_window)
        try:
            (display_x1, display_y1, display_x2, display_y2) = (
                int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
            )
        except Exception as e:
            print "Could not parse '{}'".format(options.display_window)
            raise

    pf = get_defined_playfield(ast)
    if pf is None:
        if not options.initial_configuration:
            print "source file does not define an initial configuration,"
            print "and no cellular automaton configuration file given"
            sys.exit(1)
        with open(options.initial_configuration) as f:
            pf = Playfield(default_state, repr_map)
            pf.load(f)

    count = 0

    def print_divider():
        # TODO: allow formatting string in the divider, esp.
        # to show the # of this generation
        if options.divider != '':
            print options.divider

    def begin_output():
        if not options.write_discrete_files_to:
            print_divider()

    if options.stylesheet:
        stylesheet = open(options.stylesheet).read()
    else:
        stylesheet = None

    def output_frame(count, pf):
        if options.display_window:
            if options.display_svg:
                rendered = pf.to_svg(display_x1, display_y1, display_x2, display_y2, stylesheet=stylesheet)
            else:
                rendered = pf.to_str(display_x1, display_y1, display_x2, display_y2)
        else:
            if options.display_svg:
                rendered = pf.to_svg(pf.min_x, pf.min_y, pf.max_x, pf.max_y, stylesheet=stylesheet)
            else:
                rendered = str(pf)

        if options.write_discrete_files_to:
            with open(os.path.join(options.write_discrete_files_to, "%08d.txt" % count), 'w') as f:
                f.write(rendered)
        else:
            sys.stdout.write(rendered)
            print_divider()

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
