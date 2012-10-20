ALPACA
======

This is the reference distribution for the ALPACA cellular-automaton
definition language.

ALPACA is an acronym for **a** **l**anguage for the **p**ithy
**a**rticulation of **c**ellular **a**utomata.  It is capable of
succinctly expressing the rules of a 1- or 2-dimensional cellular
automaton.

As an example, here is John Conway's Game of Life automaton, expressed
in ALPACA (it's short):

    state Dead  " "
      to Alive when 3 Alive and 5 Dead;
    state Alive "*"
      to Dead when 4 Alive or 7 Dead.

See the file `ALPACA.markdown` in the `doc` directory for a complete
description of the ALPACA language.

This distribution also contains a compiler for ALPACA, written in Perl.
It is `alpaca.pl` in the `src` directory.  It is subject to move, be
updated, or deprecated, as we define the next version of the language.

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
version 1.0.  The Perl compiler will likely be deprecated.  A new
compiler and/or interpreter will be developed, likely in some other
language.
