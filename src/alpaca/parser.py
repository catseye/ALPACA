from alpaca.ast import AST
from alpaca.scanner import Scanner

"""
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
AdjacencyFunc   ::= natural-number ["in" (Neigbourhood | NeighbourhoodID)]
                    (StateReferent | ClassReferent).
BoolPrimitive   ::= "true" | "false" | "guess".

Neighbourhood   ::= "(" {arrow-chain} ")".
"""

class Parser(object):
    def __init__(self, text):
        self.scanner = Scanner(text)

    def alpaca(self):
        entries = []
        entries.append(self.entry())
        while self.scanner.consume(';'):
            entries.append(self.entry())
        if self.scanner.consume('begin'):
            # XXX read playfield
            pass
        else:
            self.scanner.expect('.')
        return entries

    def entry(self):
        if self.scanner.on('state'):
            return self.state_defn()
        elif self.scanner.on('class'):
            return self.class_defn()
        elif self.scanner.on('neighbourhood'):
            return self.neighbourhood_defn()
        else:
            # XXX complain
            pass
    
    def state_defn(self):
        self.scanner.expect('state')
        id = self.scanner.consume_type('identifier')
        # XXX todo alternate representations
        repr = self.scanner.consume_type('string literal')
        classes = []
        while self.scanner.consume('is'):
            classes.append(self.scanner.consume_type('identifier'))
        rules = self.rules()
        return AST('StateDefn', rules, value=id)

    def class_defn(self):
        self.scanner.expect('class')
        id = self.scanner.consume_type('identifier')
        classes = []
        while self.scanner.consume('is'):
            classes.append(self.scanner.consume_type('identifier'))
        rules = self.rules()
        return AST('ClassDefn', rules, value=id)

    def neighbourhood_defn(self):
        self.scanner.expect('neighbourhood')
        id = self.scanner.consume_type('identifier')
        n = self.neighbourhood()
        return AST('NeighbourhoodDefn', [n], value=id)

    def rules(self):
        r = []
        r.append(self.rule())
        while self.scanner.consume(','):
            r.append(self.rule())
        return r

    def rule(self):
        self.scanner.expect('to')
        s = self.state_ref()
        self.scanner.expect('when')
        e = self.bool_expr()
        return AST('Rule', [s, e])

    def state_ref(self):
        # XXX arrows, too
        id = self.scanner.consume_type('identifier')
        return AST('StateRef', value=id)
