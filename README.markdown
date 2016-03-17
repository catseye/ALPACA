ALPACA
======

This is the reference distribution for the ALPACA cellular-automaton
definition language.

ALPACA is an acronym for **a** **l**anguage for the **p**ithy
**a**rticulation of **c**ellular **a**utomata.  It is capable of
succinctly expressing the rules of a 1- or 2-dimensional cellular
automaton with an arbitrary neighbourhood.

As an example, here is John Conway's Game of Life automaton, expressed
in ALPACA (it's short):

    state Dead  " "
      to Alive when 3 Alive and 5 Dead;
    state Alive "*"
      to Dead when 4 Alive or 7 Dead.

See the file `ALPACA.markdown` in the `doc` directory for a complete
specification of the ALPACA language, version 1.0.  This document is
written in [Falderal][] literate test suite format; the examples given in
the spec are test cases, which can be run against an implementation.
The `test.sh` script does this.

This distribution also contains the reference implementation of ALPACA
version 1.0, written in Python.  Its source is in the `src` directory
and `bin/alpaca` is a script to start it from the command line (no
installation is required.)  See below for more information on the reference
implementation.

This distribution also contains a compiler for an older version (0.94) of
ALPACA, which is written in Perl and which compiles ALPACA descriptions
to Perl.  It can be found in the `impl/alpaca.pl` directory.  It is no longer
maintained.

[Falderal]: http://catseye.tc/node/Falderal.html

History
-------

While [RUBE][] was being developed it became clear to the author that the
"bully" approach to writing a complex cellular automaton would result in a
program extremely difficult to understand and even worse to maintain.

ALPACA was developed in order to have a terse, precise and readable
language in which to express the rules for any given cellular automaton.
It is in ALPACA, then, that [REDGREEN][], a successor to RUBE, is written.
Being described in ALPACA instead of C, the source code for REDGREEN is
easily a hundred times clearer than the knotted mess that is RUBE.

[RUBE]: http://catseye.tc/node/RUBE.html
[REDGREEN]: http://catseye.tc/node/REDGEEN.html

Other cellular automata that have been successfully described in ALPACA
include John Conway's famous Game of Life automaton, the lesser-known
WireWorld automaton, and all of Chris Pressey's later cellular automaton
designs.

The first version, 0.80, of the ALPACA compiler was written as an
attributed grammar in CoCo/R from which a C source file was generated.

This was rewritten in version 0.90 to a hand-coded compiler in Perl 5
that produces a Perl program that accepts an automaton form (a start
state) as input, in the form of an ASCII text file, and animates it
in the terminal based on the rules of the defined cellular automaton.

Versions 0.93 and 0.94 succeeded version 0.90, but did not include any
significant changes to the language, only to the reference implementation.
Versions 0.91 and 0.92 possibly existed at some point as well, but they
are now lost.

(Note that these version numbers are highly inaccurate.  Version 0.94
was not the ninety-fourth iteration of development.)

Originally, the name ALPACA was an acronym for **a** **l**anguage for
**p**rogramming **a**rbitrary **c**ellular **a**utomata.  However, as it
was recognized by the author that the cellular automata expressible in
ALPACA were far from arbitrary (limited to two dimensions and the Moore
neighbourhood), a new backronym was sought.

The currrent version of the ALPACA language is 1.0.  It has, unlike previous
versions, a relatively formal specification, including many examples which
serve as test cases.  Version 1.0 adds several new features to the language,
such as user-defined neighbourhoods and allowing a pre-defined CA
configuration to be included with the CA description.  (This last enhancement
makes ALPACA CA-complete, which is almost the same as Turing-complete except
that there is no way to define, in ALPACA, what it means for a cellular
automaton to halt.)

ALPACA 1.0 has an entirely new reference implementation, rewritten from
scratch in Python.

Reference Implementation
------------------------

The reference implementation, `bin/alpaca`, can evolve a cellular automaton,
given its rules as described in ALPACA along with an initial configuration
(which may be supplied as part of the ALPACA description itself.)  It can also
compile the ALPACA description to a program in Javascript that will evolve the
cellular automaton, although this is somewhat of a proof-of-concept feature as
of this writing.  (It passes all the test cases, but is not really
well-architected or cleaned up.)

### Testing ###

The new implementation of ALPACA in Python has been tested with:

*   Game of Life (`eg/life/src/life.alp`)
*   Wireworld (`eg/wireworld/src/wireworld.alp`)
*   [Circute](http://catseye.tc/node/Circute.html)
*   [Jaccia](http://catseye.tc/node/Jaccia.html) and
    [Jacciata](http://catseye.tc/node/Jacciata.html)
*   [Braktif](http://catseye.tc/node/Braktif.html)
*   [REDGREEN](http://catseye.tc/node/REDGREEN.html)

...and so far seems to handle all of them correctly.

### Future Work ###

*   Generalize the compiler subsystem.  It should really compile to an
    intermediate representation (IR) that looks like the AST of a generic
    procedural language.  Then there should be an optimization pass which
    eliminates obviously unnecessary code in the IR.  The final pass should
    compile the IR to Javascript, Perl, or whatever else.
*   Possibly improve the AST objects.  Currently they are very generic,
    which was useful for development, but means that children must be
    accessed by numeric index, which is not exactly self-documenting.
*   Generally clean up and document the code more.
*   Animate the given cellular automaton in the terminal, using curses.
*   Implement non-trivial fixpoint detection: if playfield matches any of
    the last _n_ playfields, then halt.
*   Implement some option to halt under other, even more complex
    circumstances, such as some portion of the playfield matching some
    pattern.
*   Add the ability to display certain values (generation number,
    coordinates of top-left corner, etc.) in divider string, by making
    it a formatting string.

### Contributors ###

*   [Chris Pressey](https://github.com/cpressey) — bulk of the implementation
*   [Xenon](https://github.com/cmura1) — implementation of the `guess` function

Future Work
-----------

Possible ways in which the language could be extended in the future:

*   Allow the halting predicate to be defined in the ALPACA description
    itself somehow.  This would make ALPACA Turing-complete.
*   Define how the presentation of the automaton could be styled using
    (a subset of) CSS stylesheets (or something very similar.)
