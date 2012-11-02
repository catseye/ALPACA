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
description of the ALPACA language.

This distribution also contains the reference implementation of ALPACA,
written in Python.  Its source is in the `src` directory and `bin/alpaca` is
a script to start it from the command line (no installation is required.)

This implementation can evolve a cellular automaton, given its rules as
described in ALPACA, plus an initial configuration (which may be supplied
by the ALPACA description.)  

In the future this implementation may also be able to animate a cellular
automaton (probably in a terminal, using curses) and may be able to compile
an ALPACA description into the rules for evolving the cellular automaton as
code in a high-level programming language such as Python or Javascript.

This distribution also contains a compiler for an older version (v0.9x) of
ALPACA, which is written in Perl and which compiles ALPACA descriptions
to Perl.  It can be found in the `impl/alpaca.pl` directory.  It is no longer
maintained.

History
-------

While [RUBE](http://catseye.tc/node/RUBE.html) was being developed it became
clear to the author that the "bully" approach to writing a complex cellular
automaton would result in a program extremely difficult to understand and even
worse to maintain.

ALPACA was developed in order to have a terse, precise and readable
language in which to express the rules for any given cellular automaton.
It is in ALPACA, then, that [REDGREEN](http://catseye.tc/node/REDGEEN.html),
a successor to RUBE, is written. Being described in ALPACA instead of C,
the source code for REDGREEN is easily a hundred times clearer than the
knotted mess that is RUBE.

Other cellular automata that have been successfully described in ALPACA
include John Conway's famous Game of Life automaton and the lesser-known
WireWorld automaton.

The first version of the ALPACA compiler, v0.80 was written as an
attributed grammar in CoCo/R from which a C source file was generated.

This was rewritten in version 0.90 to a hand-coded compiler in Perl 5
that produces a Perl program that accepts an automaton form (a start
state) as input, in the form of an ASCII text file, and animates it
based on the rules of the defined cellular automaton.

We are currently working on a more formal specification for ALPACA
version 1.0.  It is almost complete, and adds several new features to the
language, such as user-defined neighbourhoods, representations outside
the realm of ASCII characters, and allowing a pre-defined CA configuration
to be included with the CA description (making ALPACA Turing-complete.)
For this language update, a new reference implementation was written, in
Python.

Tested
------

The new implementation of ALPACA in Python (TODO: update the above!)
has been tested with:

* Game of Life
* Wireworld
* Circute
* Jaccia and Jacciata
* Braktif

...and so far seems to handle all of them correctly.

TODO (implementation)
---------------------

* implement classes in Adjacency, for REDGREEN.
* tests for, then implement, deep inheritance (class is a class)
* clean up / document AST
* compile to Javascript
* compiler backend framework to allow compiling to other formats
* compile to legacy Perl
