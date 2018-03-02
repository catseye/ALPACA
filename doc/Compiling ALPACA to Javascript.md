Compiling ALPACA to Javascript
==============================

The reference implementation is able to compile an ALPACA description to
a set of Javascript functions which, when called, will evolve a form for
that cellular automaton.

These functions assume each generation is stored in a data structure
called a playfield, which has two methods:

*   `get(x, y)`: retrieve the name of the state at (x, y)
*   `map(new_pf, fun, min_x, min_y, max_x, max_y)`: apply `fun`
    to every cell of the playfield to obtain a new playfield

In addition, if the ALPACA description supplies an initial playfield,
the Javascript compiler will generate two `var` variables:

*   `defaultCell`, which is a string that contains the name of the state
    that cells that have never been modified assume by default
*   `initialPlayfield`, which is an array of triples (3-element arrays);
    each triple consists of x co-ordinate, y co-ordinate, and state name.

(Further info TBW)
