The ALPACA Cellular Automaton Definition Language
=================================================

This document aims to describe version 1.0 of the ALPACA language.
It is currently a work in progress.

Stuff
-----

In brief, a description of a Cellular Automaton (CA) in ALPACA consists
of a number of state or class declarations, seperated with semicolons
and ending with a period.

A state declaration defines a state, associates a visual element with it
(currently an ASCII character, possibly someday a colour or graphic) and
is followed by a list of transition rules seperated by commas.

A class declaration defines a class of states. Each state can belong to
many classes, and are listed in overload order. Classes can have their
own rules, and the `is` operator can be used to check for any of the
states of a class instead of a single state.

A transition rule specifies a state to change to and a boolean
expression to evaluate to see if that state should be changed to. The
expression may make use of whether there are a certain minimum number of
neighbours of a state or class, whether neighbours in certain positions
hold a certain state or class, and constant true, false, and random
boolean terms, manipulated by infix boolean operators.

Grammar
-------

Whitespace is ignored between tokens, and comments extend from
`/*` to `*/` and do not nest.

    AlpacaProgram   ::= Entries ".".
    Entries         ::= Entry {";" Entry}.
    Entry           ::= Class | State.
    Class           ::= "class" ClassID {ClassDesignator} [Rules].
    State           ::= "state" StateID [Appearance] {ClassDesignator} [Rules].

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
