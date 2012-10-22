The ALPACA Cellular Automaton Definition Language
=================================================

This document aims to describe version 1.0 of the ALPACA language.
It is currently a work in progress.  Thus it is referred to as version
1.0-PRE.

The language described herein is mostly compatible with the version
of the language which has existed until now (version 0.9x).  However, it
extends it in some significant ways, and is backwards-incompatible with it
in certain minor ways.  An implementation of 1.0-PRE does not yet exist.

Encoding
--------

The encoding of the text of an ALPACA description is not defined; any
encoding may be used.  However, for interchange purposes, ALPACA
descriptions are typically encoded in UTF-8 and contained in text files.

Syntax
------

An ALPACA description consists of a list of one or more _definitions_,
optionally followed by an _initial configuration_.

Each definition may specify either a _state_, a _class_, or a _neighbourhood_.
The definitions in the list are separated with semicolons, and the list ends
with either a period (if no initial configuration is given) or the token
`begin` (which introduces the initial configuration.)

Example: a trivial ALPACA description with two states:

    state Space;
    state Thing.

### States ###

A state definition gives the name of the state, zero or more _representation
declarations_ associated with the state, a list of zero or more _class
memberships_, and a comma-separated list of zero or more _transition rules_
for the state.

#### Representation Declarations ####

Each representation declaration may be a single printable ASCII character
enclosed in double quotes, or it may be a datum tagged with a name.  The tag
declares the purpose and/or the intended interpretation of the datum.  The
tag may be drawn from a set defined by this specification, or it may be
implementation-defined.  The datum may consist of essentially arbitrary data,
and may refer to a character, a colour, a graphic image, or anything else.

Representation declarations are not required.  If omitted, representation
information can be supplied by the implementation, or can be defined with
external configuration files ("skins" or "themes".)  Even if representation
declarations are included in the ALPACA description, there is nothing to
prevent an implementation from overriding them with some other representation.

However, if an initial configuration is included, it will be interpreted
using the single ASCII character representation declarations of the states.

Example: a trivial ALPACA description with single character representation
declarations:

    state Space " ";
    state Thing "*".

Example: a trivial ALPACA description with tagged-data representation
declarations:

    state Space colour:"black";
    state Thing image: "http://example.com/thing.gif".

Representation declarations generally specify a visual representation.
However, to drive home that this is not necessarily the case, the
verbiage "visual" and "appearance" has been avoided in this specification.

#### Class Memberships ####

Any number of classes may be named after the representation declarations,
with the name of each class preceded by `is`.  More information on this
will be given in the "Classes" section below.

#### Transition Rules ####

Each transition rule begins with `to`, gives a _state referent_ which
specifes the state to which to transition, followed by `when` and a _boolean
expression_ describing the conditions under which the transition occurs.

Example: a simple ALPACA description where the states have trivial
transition rules.  The result is an automaton where all cells toggle their
state from `Space` to `Thing` on every tick.

    state Space
      to Thing when true;
    state Thing
      to Space when true.

During evolution of the cellular automaton, transition rules are evaluated
in source-code order; as soon as one transition rule is found to apply, the
remaining transition rules are ignored.

If no transition rule is found to apply for a state, the default transition
will apply, which is no transition at all, i.e., remain in the same state.

##### State Referents #####

A state referent may be:

*   the name of a defined state, to refer to that state directly
*   `me`, to refer to the current state
*   a chain of _arrows_, to refer to the state of the cell found at
    that relative position in the playfield

Example: a somewhat less simple ALPACA description.  Here the states
have transition rules that cause each cell to take on the state of the
cell to the "north" (immediately above it.)  The effect would be to
make any form in this cellular automaton "scroll downwards":

    state Space
      to ^ when true;
    state Thing
      to ^ when true.

An arrow is either `^` (referring to one cell "north" or "above" the
current cell,) `v` (one cell "south" or "below",) `<` (one cell "west"
or "to the left",) or `>` (one cell "east" or "to the right".)  An arrow
sequence is a single token; it may not include whitespace.  The
arrow chain may be redundant; for example, `>>v<<^` is simply an alias
for `me`.  However, an implementation is encouraged to produce warnings
when encountering a redundant arrow-chain.

Example: an ALPACA description of a cellular automaton where `Thing`
elements grow "streaks" to the northwest (diagonally up and to the left.)

    state Space
      to Thing when v> Thing,
      to Space when true;
    state Thing
      to Thing when true.

##### Boolean Expressions #####

The boolean expression may be:

*   the constant `true` or the constant `false`
*   the nullary function `guess`, which randomly evaluates to either
    `true` or `false` (50% chance of each) each time it is evaluated
*   a _state comparison_, described below
*   a _class-inclusion comparison_, described below
*   an _adjacency comparison_, described below
*   a boolean expression preceded by the prefix operator `not`, which
    has its usual meaning
*   two boolean expressions joined by one of the infix operators
    `and`, `or,` or `xor`, which have their usual meanings
*   a parenthesized boolean expression (to change precedence rules.)

A state comparison is an expression consisting of a state referent
and another state referent.  It evaluates to true if the two state
referents refer to the same state.

Example: a cellular automaton where `Thing`s become `Spaces` only
if the cell to the east is a `Thing`:

    state Space
      to Space when true;
    state Thing
      to Space when > Thing,
      to Thing when true.

For more clarity, an equals sign may occur between the two state referents.

Example: a cellular automaton where `Thing`s become `Space`s only
if the cell to the north and the cell to the south are the same state:

    state Space
      to Space when true;
    state Thing
      to Space when ^ = v,
      to Thing when true.

A class-inclusion comparison is similar to a state comparison, but instead
of a state referent, the second term is a class referent.  An example will
be given under "Classes", below.

An adjacency comparison is an expression consisting of an integer greater
than or equal to 1, followed by an optional neighbourhood specifier,
followed by a state or class referent.  It evaluates to true only if the
cell has at least that many neighbours of that state or class, in that
neighbourhood.  If no neighbourhood is given, a Moore neighbourhood is
assumed.  Neighbourhoods are explained in more depth in the "Neighbourhoods"
section.

Example: a cellular automaton where `Thing`s become `Space`s only if they
are not adjacent to three other `Thing`s.

    state Space
      to Space when true;
    state Thing
      to Space when not 3 Thing.

Please refer to the grammar for the associativeness and precedence of the
boolean operators.

### Classes ###

A class declaration defines the general behaviour of a number of states.
Classes can have their own rules, and these are shared by all states which
are members of the class.

Example: a cellular automaton with three states, two of which are members
of the same class.  `Cat` and `Dog` will behave differently when there is
a state of the other type to the north, but they will both turn into
`Space` when there is a `Space` to the east.

    state Space
      to Space when true;
    class Animal
      to Space when > Space;
    state Dog is Animal
      to Cat when ^ Cat;
    state Cat is Animal
      to Dog when ^ Dog.

Each state can belong to zero or more classes.  When it belongs to more
than one, class the transition rules for each class are applied in order
the classes are listed in the state definition.  In addition, the transition
rules for the state itself are always applied first, before any class rules
are considered.

Example: a cellular automaton with three states and two classes, where all
states are members of both classes, but they inherit in different orders.
In it, `One`s always remain `One`s, `Two`s always remain `Two`s, and `Three`s
always remain `Three`s.

    class AlphaType
      to One when true;
    class BetaType
      to Two when true;
    state One is AlphaType is BetaType;
    state Two is BetaType is AlphaType;
    state Three is BetaType is AlphaType
      to Three when true.

In a transition rule, a class-inclusion comparison may be used by
giving a state referent, the token `is`, and the name of a class.
This expression evaluates to true if the state so referred to is a
member of that class.

Example: (TODO describe)

    state Space
      to Space when true;
    class Animal
      to Space when > is Animal;
    state Dog is Animal
      to Cat when not ^ is Animal;
    state Cat is Animal
      to Dog when not ^ is Animal.

### Neighbourhoods ###

Example:

    neighbourhood Moore
      (< > ^ v ^> ^< v> v<);
    state Space
      to Thing when 1 Moore Thing;
    state Thing
      to Space when 3 (^ v < >) Space.

### Initial Configuration ###

The list of definitions may end either with a period or the token
`begin`.  If it is the token `begin`, the remainder of the file is
assumed to contain an initial configuration for the cellular automton
now defined.

`begin` should be followed by a newline.  Each subsequent line of text
contains characters which map to cells of the playfield in the initial
configuration.

Example: a glider, pointed northeast, in John Conway's Game of Life
automaton:

    state Dead  " "
      to Alive when 3 Alive and 5 Dead;
    state Alive "*"
      to Dead when 4 Alive or 7 Dead
    begin
     **
    * *
      *

Grammar
-------

Whitespace is ignored between tokens, and comments extend from
`/*` to `*/` and do not nest.

    AlpacaProgram   ::= Entries ("." | "begin" initial-configuration).
    Entries         ::= Entry {";" Entry}.
    Entry           ::= ClassDefinition
                      | StateDefinition
                      | NeighbourhdDef.
    ClassDefinition ::= "class" ClassID {MembershipDecl}
                        [Rules].
    StateDefinition ::= "state" StateID {ReprDecl} {MembershipDecl}
                        [Rules].
    NeighbourhdDef  ::= "neighbourhood" NeighbourhoodID
                        Neighbourhood.

    ClassID         ::= identifier.
    StateID         ::= identifier.
    NeighbourhoodID ::= identifier.
    ReprDecl        ::= quoted-char
                      | identifier ":" quoted-string.

    MembershipDecl  ::= ClassReferent.
    ClassReferent   ::= "is" ClassID.

    Rules           ::= Rule {"," Rule}.
    Rule            ::= "to" StateReferent "when" Expression.

    StateReferent   ::= StateID
                      | arrow-chain
                      | "me".

    Expression      ::= Term {("and" | "or" | "xor") Term}.
    Term            ::= AdjacencyFunc
                      | "(" Expression ")"
                      | "not" Term
                      | BoolPrimitive
                      | RelationalFunc.
    RelationalFunc  ::= StateReferent (["="] StateReferent | ClassReferent).
    AdjacencyFunc   ::= ("1" | "2" | "3" | "4" | "5" | "6" | "7" | "8")
                        [Neigbourhood | NeighbourhoodID]
                        (StateReferent | ClassReferent).
    BoolPrimitive   ::= "true" | "false" | "guess".

    Neighbourhood   ::= "(" {arrow-chain} ")".

The following are token definitions, not productions.

    quoted-char     ::= quote printable-non-quote quote.
    quoted-string   ::= quote {printable-non-quote} quote.
    identifier      ::= alpha {alpha | digit}.
    quote           ::= ["].
    alpha           ::= [a-zA-Z].
    digit           ::= [0-9].
    arrow-chain     ::= arrow {arrow}.
    arrow           ::= [^v<>].

Semantics
---------

Assuming a cellular automaton form is supplied, either in the ALPACA
description, or from an external source, that form is used as the initial
configuration of the playfield.

All cells which are not defined in this initial configuration are assumed
to be "empty".  (Ooh! tricky. in previous versions, this meant "the state
whose appearance is `" "`.  In ALPACA 1.0... not sure yet.  Also, this is
a little implementation-defined; an implementation can actually provide
an initial playfield where all cells are defined, in some regular
pattern, which just happens to most commonly be "all empty")

Each time quantum (which we'll call a "tick"), all cells in the playfield
are considered, and an empty "new playfield" is established.  The state of
each cell is examined.  Each transition rule for the state is considered in
source code order.  If any transition rule is true for that cell, the
resulting state is written into that cell in the new playfield.  After all
cells in the current playfield have been considered, the current playfield
is replaced with the new playfield, and the next tick happens.

Notes
-----

An ALPACA description consisting only of classes is valid, but somewhat
meaningless by itself.  It might be used as a "module" by some other
description, however, this spec does not define a standard way in which
that could happen.

Differences between ALPACA 1.0 and Previous Versions
----------------------------------------------------

Previous versions of ALPACA did not support tagged-datum representation
declarations, or multiple representation declarations; they supported only
a single quoted character to be used as the "appearance".

Previous versions of ALPACA did not support arbitrary strings of arrows
for state designators; instead, only arrow-chains in the set {`^`, `v`, `<`,
`>`, `^<`, `^>`, `v<`, `v>`} were permitted.  In addition, previous versions
supported eight compass directions (`n`, `ne`, etc) in place of arrow chains.
This is no longer supported.  However, a future version might introduce a
more "readable" alternative state referent syntax.

Previous versions of ALPACA always assumed a Moore neighbourhood when making
an adjacency comparison.

Previous versions of ALPACA did not support giving an initial configuration
for the cellular automaton.