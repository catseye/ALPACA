The ALPACA Cellular Automaton Definition Language
=================================================

This document aims to describe version 1.0 of the ALPACA language.
It is currently a work in progress.  Thus it is referred to as version
1.0-PRE.

The language described herein is mostly compatible with the version
of the language which has existed until now (version 0.9x).  However, it
extends it in some significant ways, and is backwards-incompatible with it
in certain minor ways.  An implementation of 1.0-PRE is underway.

Abbreviations
-------------

The following abbreviations are used in this document (particularly in the
grammar production rules) and the reference implementation.

* _decl_ -- Declaration
* _defn_ -- Definition
* _nbhd_ -- Neighbourhood
* _pred_ -- Predicate
* _ref_  -- Referent
* _repr_ -- Representation

Encoding
--------

The encoding of the text of an ALPACA description is not defined; any
encoding may be used.  However, for interchange purposes, ALPACA
descriptions are typically encoded in UTF-8 and contained in text files.

Syntax
------

    -> Tests for functionality "Parse ALPACA Description"

An ALPACA description consists of a list of one or more _definitions_,
optionally followed by an _initial configuration_.

Each definition may specify either a _state_, a _class_, or a _neighbourhood_.
The definitions in the list are separated with semicolons, and the list ends
with either a period (if no initial configuration is given) or the token
`begin` (which introduces the initial configuration.)

Example: a trivial ALPACA description with two states:

    | state Space;
    | state Thing.
    = ok

### States ###

A state definition gives the name of the state, an optional _representation
declaration_ associated with the state, a list of zero or more _class
memberships_, and a comma-separated list of zero or more _transition rules_
for the state.

#### Representation Declaration ####

A representation declaration consists of an optional single printable ASCII
character enclosed in double quotes, followed by an optional comma-separated
list of _attributes_ enclosed in curly braces.

An attribute consists of a _key_ and a _value_.  The key declares the purpose
and/or the intended interpretation of the value, which is a double-quoted
string literal.  The key may be drawn from a set TBD by this specification,
or it may be implementation-defined.  The value may consist of essentially
arbitrary string data, and may refer to a character, a colour, a graphic
image, or anything else.

Representation declarations are not required.  If omitted, representation
information can be supplied by the implementation, or can be defined with
external configuration files ("skins" or "themes".)  Even if representation
declarations are included in the ALPACA description, there is nothing to
prevent an implementation from overriding them with some other representation.

However, if an initial configuration is included, it will be interpreted
using the single ASCII character representation declarations of the states.

Example: a trivial ALPACA description with single character representation
declarations:

    | state Space " ";
    | state Thing "*".
    = ok

Example: a trivial ALPACA description with representation declarations
composed of attributes:

    | state Space { colour: "black" };
    | state Thing { image:  "http://example.com/thing.gif" }.
    = ok

Example: a trivial ALPACA description with both single character and
attribute representation declarations:

    | state Space " " { color:  "black" };
    | state Thing "x" { image:  "http://example.com/thing.gif",
    |                   border: "1px solid green" }.
    = ok

Representation declarations generally specify a visual representation.
However, to drive home that this is not necessarily the case, the
verbiage "visual" and "appearance" has been avoided in this specification.

#### Aside: Initial Configuration ####

    -> Tests for functionality "Evolve ALPACA CA one generation"

We describe the initial configuration now, as it will be useful for
demonstrating the meanings of things in the core ALPACA description in
the examples to follow.

The list of definitions may end either with a period or the token
`begin`.  If it is the token `begin`, the remainder of the file is
assumed to contain an initial configuration for the cellular automton
now defined.

`begin` should be followed by a newline.  Each subsequent line of text
contains characters which map to cells of the playfield in the initial
configuration.

Example:

    | state Space " ";
    | state Thing "*"
    | begin
    |  *
    | ***
    |  *
    = -----
    =  * 
    = ***
    =  * 
    = -----

#### Class Memberships ####

Any number of classes may be named after the representation declarations,
with the name of each class preceded by `is`.  More information on this
will be given in the "Classes" section below.

#### Transition Rules ####

    -> Tests for functionality "Parse ALPACA Description"

Each transition rule begins with `to`, gives a _state referent_ which
specifes the state to which to transition, optionally followed by `when` and
a _boolean expression_ describing the conditions under which the transition
occurs.

Example: a simple ALPACA description where the states have trivial
transition rules.  The result is an automaton where all cells toggle their
state from `Space` to `Thing` on every tick.

    | state Space
    |   to Thing when true;
    | state Thing
    |   to Space when true.
    = ok

If `when` is omitted, `when true` is assumed, so the above example could
also be written:

    | state Space to Thing; state Thing to Space.
    = ok

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

    | state Space
    |   to ^ when true;
    | state Thing
    |   to ^ when true.
    = ok

An arrow is either `^` (referring to one cell "north" or "above" the
current cell,) `v` (one cell "south" or "below",) `<` (one cell "west"
or "to the left",) or `>` (one cell "east" or "to the right".)  An arrow
sequence is a single token; it may not include whitespace.  The
arrow chain may be redundant; for example, `>>v<<^` is simply an alias
for `me`.  However, an implementation is encouraged to produce warnings
when encountering a redundant arrow-chain.

Example: an ALPACA description of a cellular automaton where `Thing`
elements grow "streaks" to the northwest (diagonally up and to the left.)

    | state Space
    |   to Thing when v> Thing;
    | state Thing.
    = ok

##### Boolean Expressions #####

The boolean expression may be:

*   the constant `true` or the constant `false`
*   the nullary function `guess`, which randomly evaluates to either
    `true` or `false` (50% chance of each) each time it is evaluated
*   a _state predicate_, described below
*   a _class-inclusion predicate_, described below
*   an _adjacency predicate_, described below
*   a boolean expression preceded by the prefix operator `not`, which
    has its usual meaning
*   two boolean expressions joined by one of the infix operators
    `and`, `or,` or `xor`, which have their usual meanings
*   a parenthesized boolean expression (to change precedence rules.)

Please refer to the grammar for the associativeness and precedence of the
boolean operators.

A state predicate is an expression consisting of a state referent
and another state referent.  It evaluates to true if the two state
referents refer to the same state.

Example: a cellular automaton where `Thing`s become `Spaces` only
if the cell to the east is a `Thing`:

    | state Space;
    | state Thing
    |   to Space when > Thing.
    = ok

For more clarity, an equals sign may occur between the two state referents.

Example: a cellular automaton where `Thing`s become `Space`s only
if the cell to the north and the cell to the south are the same state:

    | state Space;
    | state Thing
    |   to Space when ^ = v.
    = ok

A class-inclusion predicate is similar to a state predicate, but instead
of a state referent, the second term is a class referent.  An example will
be given under "Classes", below.

State predicates and class-inclusion predicates are collectively known as
_relational predicates_.

An adjacency predicate is an expression consisting of an integer greater
than or equal to 1, followed by an optional neighbourhood specifier,
followed by a state or class referent.  It evaluates to true only if the
cell has at least that many neighbours of that state or class, in that
neighbourhood.  If no neighbourhood is given, a Moore neighbourhood is
assumed.  Neighbourhoods are explained in more depth in the "Neighbourhoods"
section.

Example: a cellular automaton where `Thing`s become `Space`s only if they
are not adjacent to three other `Thing`s.

    | state Space;
    | state Thing
    |   to Space when not 3 Thing.
    = ok

### Classes ###

A class declaration defines the general behaviour of a number of states.
Classes can have their own rules, and these are shared by all states which
are members of the class.

Example: a cellular automaton with three states, two of which are members
of the same class.  `Cat` and `Dog` will behave differently when there is
a state of the other type to the north, but they will both turn into
`Space` when there is a `Space` to the east.

    | state Space;
    | class Animal
    |   to Space when > Space;
    | state Dog is Animal
    |   to Cat when ^ Cat;
    | state Cat is Animal
    |   to Dog when ^ Dog.
    = ok

Each state can belong to zero or more classes.  When it belongs to more
than one, class the transition rules for each class are applied in order
the classes are listed in the state definition.  In addition, the transition
rules for the state itself are always applied first, before any class rules
are considered.

Example: a cellular automaton with three states and two classes, where all
states are members of both classes, but they inherit in different orders.
In it, `One`s always remain `One`s, `Two`s always remain `Two`s, and `Three`s
always remain `Three`s.

    | class AlphaType
    |   to One when true;
    | class BetaType
    |   to Two when true;
    | state One is AlphaType is BetaType;
    | state Two is BetaType is AlphaType;
    | state Three is BetaType is AlphaType
    |   to Three when true.
    = ok

In a transition rule, a class-inclusion predicate may be used by
giving a state referent, the token `is`, and the name of a class.
This expression evaluates to true if the state so referred to is a
member of that class.

Example: a cellular automaton where `Dog`s and `Cat`s (both `Animal`s)
switch to the other when the cell to the north is not an `Animal` and turn
to `Space` when the cell to the east is an `Animal`.

    | state Space;
    | class Animal
    |   to Space when > is Animal;
    | state Dog is Animal
    |   to Cat when not ^ is Animal;
    | state Cat is Animal
    |   to Dog when not ^ is Animal.
    = ok

### Neighbourhoods ###

A neighbourhood is a set of positions relative to a cell.  A neighbourhood
is specified in ALPACA with a sequence of arrow chains inside parentheses.
A neighbourhood definition associates a neighbourhood with a name, so that
whereever a neighbourhood can be specified, the name can be used instead.

A neighbourhood can be specified in an adjacency predicate.  If none is
specified in an adjacency predicate, the Moore neighbourhood (as defined
in the below example) is used.

Example:

    | neighbourhood Moore
    |   (< > ^ v ^> ^< v> v<);
    | neighbourhood VonNeumann
    |   (^ v < >);
    | state Space
    |   to Thing when 1 in Moore Thing;
    | state Thing
    |   to Space when 3 in (^ v < >) Space.
    = ok

(TODO: the following example is out of place)

Example: a glider, pointed northeast, in John Conway's Game of Life
automaton:

    | state Dead  " "
    |   to Alive when 3 Alive and 5 Dead;
    | state Alive "*"
    |   to Dead when 4 Alive or 7 Dead
    | begin
    |  **
    | * *
    |   *
    = ok

Grammar
-------

Whitespace is ignored between tokens, and comments extend from
`/*` to `*/` and do not nest.

    Alpaca          ::= Defns ("." | "begin" initial-configuration).
    Defns           ::= Defn {";" Defn}.
    Defn            ::= StateDefn
                      | ClassDefn
                      | NbhdDefn.
    StateDefn       ::= "state" StateID [quoted-char] [ReprDecl]
                        {MembershipDecl}
                        [Rules].
    ClassDefn       ::= "class" ClassID
                        {MembershipDecl}
                        [Rules].
    NbhdDefn        ::= "neighbourhood" NbhdID
                        Neighbourhood.

    ClassID         ::= identifier.
    StateID         ::= identifier.
    NbhdID          ::= identifier.

    ReprDecl        ::= "{" Attribute {"," Attribute} "}".
    Attribute       ::= identifier ":" quoted-string.

    MembershipDecl  ::= ClassRef.
    ClassRef        ::= "is" ClassID.

    Rules           ::= Rule {"," Rule}.
    Rule            ::= "to" StateRef ["when" Expression].

    StateRef        ::= StateID
                      | arrow-chain
                      | "me".

    Expression      ::= Term {("and" | "or" | "xor") Term}.
    Term            ::= AdjacencyPred
                      | "(" Expression ")"
                      | "not" Term
                      | BoolPrimitive
                      | RelationalPred.
    RelationalPred  ::= StateRef (["="] StateRef | ClassRef).
    AdjacencyPred   ::= natural-number ["in" (Neigbourhood | NbhdID)]
                        (StateRef | ClassRef).
    BoolPrimitive   ::= "true" | "false" | "guess".

    Neighbourhood   ::= "(" {arrow-chain} ")".

The following are token definitions, not productions.

    quoted-char     ::= quote printable-non-quote quote.
    quoted-string   ::= quote {printable-non-quote} quote.
    identifier      ::= alpha {alpha | digit}.
    natural-number  ::= digit {digit}.
    quote           ::= ["].
    alpha           ::= [a-zA-Z].
    digit           ::= [0-9].
    arrow-chain     ::= arrow {arrow}.
    arrow           ::= [^v<>].
    initial-config  ::= <<the remainder of the file>>.

Semantics
---------

Assuming a cellular automaton form is supplied, either in the ALPACA
description, or from an external source, that form is used as the initial
configuration of the playfield.

All cells which are not defined in this initial configuration are assigned
states in an implementation-dependent manner which we will call _empty_.

An implementation should at a minimum support populating the undefined area
of the playfield uniformly with the first state defined in the ALPACA
description.  An informal survey of extant ALPACA descriptions suggested that
the first defined state is the one that is most commonly assumed to permeate
"everywhere else" in the playfield and represent emptiness.

Of course, an implementation may support, beyond this bare minimum, populating
the space outside the given configuration with any pattern it sees fit.
ALPACA does not (yet) support specifying this pattern, so emptiness is
entirely implementation-dependent.

Each time quantum (which we'll call a _tick_), all cells in the playfield
are considered, and an empty "new playfield" is established.  The state of
each cell is examined.  Each transition rule for the state is considered in
source code order.  If any transition rule is true for that cell, the
resulting state is written into that cell in the new playfield.  After all
cells in the current playfield have been considered, the current playfield
is replaced with the new playfield, and the next tick happens.

Notes
-----

An ALPACA description consisting only of classes and/or neighbourhoods is
valid, but somewhat meaningless by itself.  It might be used as a "module"
by some other description, however, this spec does not define a standard
way in which that could happen.

`arrow-chain` and `identifier` tokens overlap; tokens beginning with a
series of `v`s (lower-case letter "vee"s) will be interpreted as an `arrow-chain`.
Thus, the text `vonNeumann` will be scanned as the arrow-chain `v` followed
by the identifier `onNeumann`.  Until such time as this is addressed, avoid
giving states, classes, and neighbourhoods names which begin with a lowercase
`v`.  (Convention says to start these identifiers with uppercase letters
anyhow.)

Differences between ALPACA 1.0 and Previous Versions
----------------------------------------------------

Previous versions of ALPACA did not support attribute representation
declarations, or multiple representation declarations; they supported only
a single quoted character to be used as the "appearance".

Previous versions of ALPACA did not support arbitrary strings of arrows
for state designators; instead, only arrow-chains in the set {`^`, `v`, `<`,
`>`, `^<`, `^>`, `v<`, `v>`} were permitted.  In addition, previous versions
supported eight compass directions (`n`, `ne`, etc) in place of arrow chains.
This is no longer supported.  However, a future version might introduce a
more "readable" alternative state referent syntax.

Previous versions of ALPACA always assumed a Moore neighbourhood when making
an adjacency predicate.

Previous versions of ALPACA did not support giving an initial configuration
for the cellular automaton.
