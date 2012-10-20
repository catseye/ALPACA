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
elements_ associated with the state, and a comma-separated list of zero or
more _transition rules_ for the state.

#### Representation Elements ####

Each representation element may be a single UTF-8 character enclosed in
quotes, or it may be a datum tagged with a name.  The tag declares the
purpose and/or the intended interpretation of the datum.  The tag may be
drawn from a set defined by this specification, or it may be
implementation-defined.  The datum may consist essentially arbitrary data,
and may refer to a character, a colour, a graphic image, or anything else.

Representation elements are not required.  In this case, representation
information can be supplied by the implementation, or can be defined with
external configuration files ("skins" or "themes".)  Even if representation
elements are included, there is nothing preventing an implementation from
overriding them with some other representation.

Example: a trivial ALPACA description with single character representation
elements:

    state Space " ";
    state Thing "*".

Example: a trivial ALPACA description with tagged-data representation
elements:

    state Space colour:black;
    state Thing image:"http://example.com/thing.gif".

#### Transition Rules ####

Each transition rule specifies a boolean expression describing the
conditions under which the transition occurs, and the state to which to
change under those conditions.  The expression may make use of whether
there are a certain minimum number of neighbours of a state or class,
whether neighbours in certain positions hold a certain state or class,
and constant true, false, and random boolean terms, manipulated by infix
boolean operators.

Example: a simple ALPACA description where the states have trivial
transition rules:

    state Space
      to Thing;
    state Thing
      to Space.

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
    State           ::= "state" StateID [Appearance] {ClassDesignator}
                        [Rules].

    ClassID         ::= identifier.
    StateID         ::= identifier.
    Appearance      ::= character.

    ClassDesignator ::= "is" ClassID.

    Rules           ::= Rule {"," Rule}.
    Rule            ::= "to" StateDesignator "when" Expression.

    Expression      ::= Term {("and" | "or" | "xor") Term}.

    Term            ::= AdjacentcyFunc
                      | "(" Expression ")"
                      | "not" Term
                      | BoolPrimitive
                      | RelationalFunc.

    RelationalFunc  ::= StateDesignator (StateDesignator | ClassDesignator).

    StateDesignator ::= "n" | "^" | "nw" | "^<"
                      | "s" | "v" | "ne" | "^>"
                      | "w" | "<" | "sw" | "v<"
                      | "e" | ">" | "se" | "v>" | "me" | StateID.

    AdjacentcyFunc  ::= ("1" | "2" | "3" | "4" | "5" | "6" | "7" | "8")
                        (StateDesignator | ClassDesignator).

    BoolPrimitive   ::= "true" | "false" | "guess".

    character       ::= quote printable-non-quote quote.
    identifier      ::= alpha {alpha | digit}.
