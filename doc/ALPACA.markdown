The ALPACA Cellular Automaton Definition Language
=================================================

This document describes version 1.1 of ALPACA, a language for defining
cellular automata.

The language described herein is mostly compatible with the legacy
version (0.9x) of the language as it has existed for many years (since
1998), with only some additions and only a small number of backwards-
incompatible changes, and it is entirely backwards-compatible with
version 1.0 (released 2013).

The reference implementation of ALPACA version 1.1 that accompanies
this specification is included in the ALPACA reference distribution.

In the remainder of this document, ALPACA refers to ALPACA version 1.1.

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

Each definition associates a defined object with a _name_.  A name is an
alphabetic character followed by zero or more alphanumeric characters with
no other intervening characters.  A name may not be any of the 16 reserved
keywords defined by ALPACA, which are:

    and          neighbourhood
    begin        not
    class        or
    false        state
    guess        to
    in           true
    is           when
    me           xor

Example: a trivial ALPACA description with two states and no initial
configuration:

    | state Space;
    | state Thing.
    = ok

### States ###

A state definition gives the name of the state, an optional _representation
declaration_ associated with the state, a list of zero or more _class
memberships_, and a comma-separated list of zero or more _transition rules_
for the state.

#### Representation Declaration ####

A representation declaration consists of a single non-combining Unicode
character enclosed in double quotes.

A representation declaration is not required for any given state.  However,
if an initial configuration is included in the ALPACA description, the
characters in it will be mapped to states by using the representation
declaration of each state.  Therefore, if a state has no representation
declaration, no cell in that state can be present in the initial
configuration.

No two states may have the same representation declaration.

Informational: an implementation may use the representation declaration of
a state to display (or otherwise communicate) that state to the user.  This
is certainly a reasonable choice, and one expects many implementations will
at least offer that as an option.  However, representation of states is
ultimately implementation-defined.  Even if representation declarations are
included for every state in the ALPACA description, there is nothing to
prevent an implementation from overriding them with some other representation.
See also the section on ALPACA Stylesheets, below.

Example: a trivial ALPACA description with single character representation
declarations:

    | state Space " ";
    | state Thing "*".
    = ok

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

In a state definition, any number of classes may be named after the
representation declaration, with the name of each class preceded by `is`.
More information on this will be given in the "Classes" section below.

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

    -> Tests for functionality "Evolve ALPACA CA one generation"

A state referent may be:

*   the name of a defined state, to refer to that state directly
*   `me`, to refer to the current state
*   a chain of _arrows_, to refer to the state of the cell found at
    that relative position in the playfield

Example: a somewhat less simple ALPACA description.  Here the (non-empty)
states have transition rules that cause each cell to take on the state of one
of its neighbours; `Up` cells take on the state of the cell to the "north"
(immediately above it) while `Down` cells take on the state of the cell to
the "south" (immediately below it.)  The effect in this example is for the
cells to "swap places":

    | state Space " ";
    | state Up "U"
    |   to ^ when true;
    | state Down "D"
    |   to v when true
    | begin
    | DDD
    | UUU
    = -----
    = UUU
    = DDD
    = -----

An arrow is either `^` (referring to one cell "north" or "above" the
current cell,) `v` (one cell "south" or "below",) `<` (one cell "west"
or "to the left",) or `>` (one cell "east" or "to the right".)  An arrow
sequence is a single token; it may not include whitespace.  The
arrow chain may be redundant; for example, `>>v<<^` is simply an alias
for `me`.  However, an implementation is encouraged to produce warnings
when encountering a redundant arrow-chain.

Example: an ALPACA description of a cellular automaton where `Thing`
elements grow "streaks" to the northwest (diagonally up and to the left.)

    | state Space " "
    |   to Thing when v> Thing;
    | state Thing "*"
    | begin
    | *
    | *
    = -----
    = * 
    = **
    =  *
    = -----

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

    | state Space " ";
    | state Thing "*"
    |   to Space when > Thing
    | begin
    | *
    | **
    = -----
    = * 
    =  *
    = -----

For more clarity, an equals sign may occur between the two state referents.

Example: a cellular automaton where `Thing`s become `Space`s only
if the cell to the north and the cell to the south are the same state:

    | state Space " ";
    | state Thing "*"
    |   to Space when ^ = v
    | begin
    | *
    | **
    = -----
    = *
    = *
    = -----

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

    | state Space " ";
    | state Thing "*"
    |   to Space when not 3 Thing
    | begin
    | *
    | **
    | *
    = -----
    = **
    = -----

Example: boolean operators.

    | state Space " ";
    | state Thing "*";
    | state Charge "X";
    | state One "1"
    |   to Thing when ^ Charge and > Charge;
    | state Two "2"
    |   to Thing when ^ Charge or > Charge;
    | state Three "3"
    |   to Thing when ^ Charge xor > Charge
    | begin
    | X  X
    | 1X 1 1X 1
    | 
    | X  X
    | 2X 2 2X 2
    | 
    | X  X
    | 3X 3 3X 3
    = -----
    = X  X     
    = *X 1 1X 1
    =          
    = X  X     
    = *X * *X 2
    =          
    = X  X     
    = 3X * *X 3
    = -----

### Classes ###

A class declaration defines the general behaviour of a number of states.
Classes can have their own rules, and these are shared by all states which
are members of the class.

Example: a cellular automaton with three states, two of which are members
of the same class.  `Cat` and `Dog` will behave differently when there is
a state of the other type to the north, but they will both turn into
`Space` when there is a `Space` to the east.

    | state Space " ";
    | class Animal
    |   to Space when > Space;
    | state Dog "d" is Animal
    |   to Cat when ^ Cat;
    | state Cat "c" is Animal
    |   to Dog when ^ Dog
    | begin
    | ccd
    | dcc
    = -----
    = cc 
    = ccd
    = -----

Each state can belong to zero or more classes.  When it belongs to more
than one class, the transition rules for each class are applied in the order
the classes are listed in the state definition.  In addition, the transition
rules for the state itself are always applied first, before any class rules
are considered.

Example: a cellular automaton with three states and two classes, where all
states are members of both classes, but they inherit in different orders.
In it, `One`s and always become `Four`s, `Two`s always become `Five`s,
and `Three`s always remain `Three`s.

    | state Space " ";
    | class AlphaType
    |   to Four when true;
    | class BetaType
    |   to Five when true;
    | state One "1" is AlphaType is BetaType;
    | state Two "2" is BetaType is AlphaType;
    | state Three "3" is BetaType is AlphaType
    |   to Three when true;
    | state Four "4";
    | state Five "5"
    | begin
    | 123
    = -----
    = 453
    = -----

Example: deep inheritance.

    | state Space " ";
    | state Thing "*";
    | class Animal
    |   to Thing when > Thing;
    | class Mammal is Animal
    |   to Thing when ^ Thing;
    | state Cat "c" is Mammal
    |   to Thing when v Thing
    | begin
    |    *
    | c  c  c*  c
    | *
    = -----
    =    *       
    = *  *  **  c
    = *          
    = -----

Example: overriding deep inheritance at a class level.

    | state Space " ";
    | state Thing "*";
    | class Animal
    |   to Thing when > Thing;
    | class Mammal is Animal
    |   to Space when > Thing;
    | state Cat "c" is Mammal
    |   to Thing when v Thing
    | begin
    |    *
    | c  c  c*
    | *
    = -----
    =    *    
    = *  c   *
    = *       
    = -----

It is not an error for classes to belong to themselves, either
directly or transitively.  A class belonging to itself should
not lead to infinite regress - each class it belongs to should
only be checked once.  (Thanks to
[OrangeNote](https://github.com/OrangeNote) for this test case.)

    | class A is B to X when false;
    | class B is A to X when false;
    | 
    | state Blank " ";
    | state X "*" is A
    | 
    | begin
    | *
    = -----
    = *
    = -----

#### Membership ####

In a transition rule, a class-inclusion predicate may be used by giving a
state referent, the token `is`, and the name of a class.  This expression
evaluates to true if the state so referred to is a member of that class.

Example: a cellular automaton where `Dog`s and `Cat`s (both `Animal`s)
switch to the other when the cell to the north is not an `Animal` and turn
to `Space` when the cell to the east is an `Animal`.

    | state Space " ";
    | class Animal
    |   to Space when > is Animal;
    | state Dog "d" is Animal
    |   to Cat when not ^ is Animal;
    | state Cat "c" is Animal
    |   to Dog when not ^ is Animal
    | begin
    | dcdc
    | dcdc 
    = -----
    = cdcd
    =    c
    = -----

Class-inclusion predicates can also be used as part of adjacency
predicates.

    | state Space " ";
    | class Mineral;
    | state Granite "*" is Mineral;
    | state Iron "#" is Mineral;
    | state Wood "&"
    |   to Space when not 3 is Mineral
    | begin
    | #  * 
    | #&&&*
    | *   #
    = -----
    = #  * 
    = #& &*
    = *   #
    = -----

Class membership is transitive.

    | state Space " ";
    | class Animal;
    | class Mammal is Animal;
    | state Dog "d" is Mammal;
    | state Wood "&"
    |   to Space when not 3 is Animal;
    | state Food "."
    |   to Space when ^ is Animal
    | begin
    | d .
    | d&&
    | .dd
    = -----
    = d .
    = d& 
    =  dd
    = -----

It is possible for a class to be empty, i.e. for no states to belong to the
class.  In this case, the class inclusion predicate will always evaluate to
false.  (Thanks to [OrangeNote](https://github.com/OrangeNote) for this
test case.)

    | class A is B;
    | class B;
    | class C;
    | 
    | state Blank " ";
    | state X "*" is A
    |   to Blank when me is C
    | 
    | begin
    | *
    = -----
    = *
    = -----

Informative: diamond inheritance seems to not be a problem in practice, as
classes do not define or contain any state information which is not in the state
itself, which is what makes diamond inheritance problematic in most languages
with multiple inheritance.

### Neighbourhoods ###

    -> Tests for functionality "Parse ALPACA Description"

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

    -> Tests for functionality "Evolve ALPACA CA one generation"

Note that, unlike versions of ALPACA before 1.0, ALPACA 1.x allows essentially
arbitrary neighbourhoods -- they may extend beyond the Moore neighbourhood.
Implementations must take care to check for all possible transitions inside
the defined neighbourhood, even when it extends into the "empty space"
surrounding the defined configuration.

    | neighbourhood Distant
    |   (<<< >>> ^^^ vvv);
    | state Space " "
    |   to Thing when 1 in Distant Thing;
    | state Thing "#"
    | begin
    | #
    = -----
    =    #   
    =        
    =        
    = #  #  #
    =        
    =        
    =    #   
    = -----

Some More Realistic Examples
----------------------------

This section is not normative.

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
    = -----
    = ** 
    =  **
    = *  
    = -----

Grammar
-------

Whitespace is ignored between tokens, and comments extend from
`/*` to `*/` and do not nest.

    Alpaca          ::= Defns ("." | "begin" initial-configuration).
    Defns           ::= Defn {";" Defn}.
    Defn            ::= StateDefn
                      | ClassDefn
                      | NbhdDefn.
    StateDefn       ::= "state" StateID [quoted-char]
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
series of `v`s (lower-case letter "vee"s) will be interpreted as an
`arrow-chain`.  Thus, the text `vonNeumann` will be scanned as the arrow-chain
`v` followed by the identifier `onNeumann`.  This may be addressed in a future
version of ALPACA.  Until such time, avoid giving states, classes, and
neighbourhoods names which begin with a lowercase `v`.  (Convention says to
start these identifiers with uppercase letters anyhow.)

Differences between ALPACA 1.0 and Previous Versions
----------------------------------------------------

Previous versions of ALPACA did not support arbitrary strings of arrows
for state designators; instead, only arrow-chains in the set {`^`, `v`, `<`,
`>`, `^<`, `^>`, `v<`, `v>`} were permitted.  In addition, previous versions
supported eight compass direction abbreviations (`n`, `ne`, etc) in place of
arrow chains.  This is no longer supported.

Previous versions of ALPACA always assumed a Moore neighbourhood when making
an adjacency predicate.  Other neighbourhoods could not be defined, and
needed to be constructed in a tedious piecemeal fashion (see the Jaccia and
Jacciata descriptions for an example of this for the von Neumann
neighbourhood.)

Previous versions of ALPACA did not support giving an initial configuration
for the cellular automaton.

Differences between ALPACA 1.1 and 1.0
--------------------------------------

-   ALPACA 1.1 explicitly states that it is valid for a class to be empty.
-   ALPACA 1.1 defines what it means for a class to belong to itself, either
    directly or transitively.  This was not defined in ALPACA 1.0.
-   ALPACA 1.1 introduces ALPACA Stylesheets 1.0.

ALPACA Stylesheets 1.0
----------------------

Informational: Early efforts at defining ALPACA 1.0 wished to include a more
sophisticated mechanism for describing appearance of states, but this effort
was abandoned under the argument of "separation of content and presentation".
ALPACA Stylesheets 1.0 is a rekindled attempt to define this mechanism.

An ALPACA stylesheet is a way of specifying how the playfields of an ALPACA
cellular automaton should be represented.  A single cellular automation may
have multiple stylesheets that can be applied to it, and indeed a single
stylesheet may apply to multiple cellular automata.

Because there is currently no way to embed an ALPACA stylesheet in an ALPACA
description, an ALPACA stylesheet, if any, must be supplied as a seperate
input to whatever ALPACA-processing tools that may support it.

An ALPACA stylesheet is based on a subset of the stylesheets supported by
[SVG 1.1][].  In particular,

-   Each state in the cellular automaton maps to a CSS class.
-   The `fill` property, with a colour, is guaranteed to be supported.
-   `#rrggbb` format for colours is guaranteed to be supported.
-   No other guarantees are, at present, given.  (This includes support
    for comments.  There is no guaranteed way, at present, to include
    comments in an ALPACA Stylesheet.)
-   This does not prevent any implementation from using an extended
    definition of ALPACA Stylesheets 1.0 to apply representation to
    cellular automata.

Example:

    .Dead {
        fill: #ffffff;
    }
    .Alive {
        fill: #000000;
    }

This will style John Conway's Life with Dead cells appearing as solid
white rectangles and Alive cells appearing as solid black rectangles.

Informational: It is expected that a future version of ALPACA Stylesheets
will define a property called `glyph` that will correspond to the
character used in the Representation Declaration of an ALPACA state
(see above) with the understanding that it will be used primarily
for display, while the Representation Declaration will be used primarily
for interpreting a cellular automaton's configuration from a textual
source, e.g. the initial playfield.

[SVG 1.1]: https://www.w3.org/Graphics/SVG/1.1/
