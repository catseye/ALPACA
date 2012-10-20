The ALPACA Cellular Automaton Definition Language
=================================================

This document aims to describe version 1.0 of the ALPACA language.
It is currently a work in progress.  Thus it is referred to as version
1.0-PRE.

The language described herein is mostly compatible with the version
of language which has existed until now (version 0.9x).  However, it
extends it in some significant ways, and it may be backwards-incompatible
in certain way.  An implementation of 1.0-PRE does not yet exist.

Syntax
------

An ALPACA program consists of a list of one or more definitions, optionally
followed by an initial playfield state.

The definitions in the list are seperated with semicolons and the list
ends with a period.

Each definition may specify either a state or a class.

A state definition gives the name of the state, zero or more visual elements
associated with the state, and a list of zero or more transition rules for
the state, seperated by commas.

The visual element is currently a single ASCII character, possibly
someday a colour or graphic.

Each transition rule specifies a boolean expression describing the
conditions under which the transition occurs, and the state to which to
change under those conditions.  The expression may make use of whether
there are a certain minimum number of neighbours of a state or class,
whether neighbours in certain positions hold a certain state or class,
and constant true, false, and random boolean terms, manipulated by infix
boolean operators.

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
