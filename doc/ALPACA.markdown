The ALPACA Cellular Automaton Definition Language
=================================================

This document aims to describe version 1.0 of the ALPACA language.
It is currently a work in progress.  Thus it is referred to as version
1.0-PRE.

The language described herein is mostly compatible with the version
of language which has existed until now (version 0.9x).  However, it
extends it in some significant ways, and it may be backwards-incompatible
in certain way.  An implementation of 1.0-PRE does not yet exist.

Encoding
--------

The encoding of the text of an ALPACA description is not defined; any
encoding may be used.  However, for interchange purposes, ALPACA
descriptions are typically encoded in UTF-8.

Syntax
------

An ALPACA description consists of a list of one or more _definitions_,
optionally followed by an _initial playfield state_.

Each definition may specify either a _state_ or a _class_.  The definitions
in the list are seperated with semicolons and the list ends with a period.

Example: a trivial ALPACA description with two states:

    state Space;
    state Thing.

### States ###

A state definition gives the name of the state, zero or more _representation
declarations_ associated with the state, and a comma-separated list of zero
or more _transition rules_ for the state.

#### Representation Declarations ####

Each representation declaration may be a single UTF-8 character enclosed in
quotes, or it may be a datum tagged with a name.  The tag declares the
purpose and/or the intended interpretation of the datum.  The tag may be
drawn from a set defined by this specification, or it may be
implementation-defined.  The datum may consist essentially arbitrary data,
and may refer to a character, a colour, a graphic image, or anything else.

Representation declarations are not required.  In this case, representation
information can be supplied by the implementation, or can be defined with
external configuration files ("skins" or "themes".)  Even if representation
declarations are included, there is nothing preventing an implementation from
overriding them with some other representation.

Example: a trivial ALPACA description with single character representation
declarations:

    state Space " ";
    state Thing "*".

Example: a trivial ALPACA description with tagged-data representation
declarations:

    state Space colour:"black";
    state Thing image: "http://example.com/thing.gif".

Representation declarations generally specify a visual representation,
however, to drive home that this is not necessarily the case, the
verbiage "visual" and "appearance" has been avoided in this specification.

#### Transition Rules ####

Each transition rule begins with `to`, gives a _state referent_ which
specifes the state to which to make the transition, followed by `when` and
a _boolean expression_ describing the conditions under which the transition
occurs.

Example: a simple ALPACA description where the states have trivial
transition rules:

    state Space
      to Thing when true;
    state Thing
      to Space when true.

##### State Referents #####

The state referent may be:

*   the name of a state, to refer to that state directly
*   `me`, to refer to the current state
*   a chain of _arrows_, to refer to the state of the cell found at
    that relative position in the playfield

Example: a somewhat less simple ALPACA description.  Here the states
have transition rules that cause each cell to take on the state of the
cell to the "north" (immediately above it.)  The effect would be to
make any form in this cellular automaton "scroll downwards":

    state " " Space
      to ^ when true;
    state "*" Thing
      to ^ when true.

An arrow is either `^` (referring to one cell "north" or "above" the
current cell,) `v` (one cell "south" or "below",) `<` (one cell "west"
or "to the left",) or `>` (one cell "east" or "to the right".)  Each arrow
is its own token; they may or may not be separated with whitespace.  The
arrow chain may be redundant; for example, `>>v<<^` is simply an alias
for `me`.  However, an implementation is encouraged to produce warnings
when encountering a redundant arrow-chain.

Example: an ALPACA description of a cellular automaton where `Thing`
elements grow "streaks" to the northwest.

    state " " Space
      to Thing when v> Thing,
      to Space when true;
    state "*" Thing
      to Thing when true.

##### Boolean Expressions #####

The boolean expression may be:

*   the constant `true` or the constant `false`
*   the nullary function `guess`, which randomly evaluates to either
    `true` or `false` (50% chance of each) each time it is evaluated
*   a boolean expression preceded by the prefix operator `not`, which
    has its usual meaning
*   two boolean expressions joined by one of the infix operators
    `and`, `or,` or `xor`, which have their usual meanings
*   ...

The expression may also make use of whether
there are a certain minimum number of neighbours of a state or class,
whether neighbours in certain positions hold a certain state or class.

### Classes ###

A class declaration defines the general behaviour of a number of states.
Each state can belong to many classes, and are listed in overload order.
Classes can have their own rules, and the `is` operator can be used to
check for any of the states of a class instead of a single state.

Grammar
-------

Whitespace is ignored between tokens, and comments extend from
`/*` to `*/` and do not nest.

    AlpacaProgram   ::= Entries ".".
    Entries         ::= Entry {";" Entry}.
    Entry           ::= Class | State.
    Class           ::= "class" ClassID {ClassDesignator}
                        [Rules].
    State           ::= "state" StateID {ReprDecl} {ClassDesignator}
                        [Rules].

    ClassID         ::= identifier.
    StateID         ::= identifier.
    ReprDecl        ::= quoted-char
                      | identifier ":" quoted-string.

    ClassDesignator ::= "is" ClassID.

    Rules           ::= Rule {"," Rule}.
    Rule            ::= "to" StateReferent "when" Expression.

    StateReferent   ::= StateID
                      | Arrow {Arrow}
                      | "me".
    Arrow           ::= "^" | "v" | "<" | ">".

    Expression      ::= Term {("and" | "or" | "xor") Term}.
    Term            ::= AdjacencyFunc
                      | "(" Expression ")"
                      | "not" Term
                      | BoolPrimitive
                      | RelationalFunc.
    RelationalFunc  ::= StateReferent (StateReferent | ClassDesignator).
    AdjacencyFunc   ::= ("1" | "2" | "3" | "4" | "5" | "6" | "7" | "8")
                        (StateReferent | ClassDesignator).
    BoolPrimitive   ::= "true" | "false" | "guess".

The following are token definitions, not productions.

    quoted-char     ::= quote printable-non-quote quote.
    quoted-string   ::= quote {printable-non-quote} quote.
    identifier      ::= alpha {alpha | digit}.
    quote           ::= ["].
    alpha           ::= [a-zA-Z].
    digit           ::= [0-9].

Semantics
---------

A cellular automaton evolves.  (TODO be more specific)

Assuming a cellular automaton form is supplied, either in the ALPACA
description, or from an external source, that form is used as the initial
configuration of the playfield.

All cells which are not defined in this initial configuration are assumed
to be "empty".  (Ooh! tricky. in previous versions, this meant "the state
whose appearance is `" "`.  In ALPACA 1.0... not sure yet.  Also, this is
a little implementation-defined; an implementation can actually provide
an initial playfield where all cells are defined, in some regular
pattern, which just happens to most commonly be "all empty")

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
`>`, `^<`, `^>`, `v<`, `v>`} were pemitted (in both their arrow and
compass-direction forms.)  In addition, previous versions supported
eight compass directions (`n`, `ne`, etc) in place of arrow chains.  This
is no longer supported.  However, a future version might introduce a more
"readable" alternative state referent syntax.
