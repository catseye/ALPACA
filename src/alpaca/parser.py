from alpaca.ast import AST
from alpaca.scanner import Scanner

"""
Alpaca          ::= Definitions ("." | "begin" initial-configuration).
Definitions     ::= Definition {";" Definition}.
Definition      ::= StateDefinition
                  | ClassDefinition
                  | NeighbourhdDef.
StateDefinition ::= "state" StateID [quoted-char] [ReprDecl]
                    {MembershipDecl}
                    [Rules].
ClassDefinition ::= "class" ClassID
                    {MembershipDecl}
                    [Rules].
NeighbourhdDef  ::= "neighbourhood" NeighbourhoodID
                    Neighbourhood.

ClassID         ::= identifier.
StateID         ::= identifier.
NeighbourhoodID ::= identifier.

ReprDecl        ::= "{" TaggedDatum {"," TaggedDatum} "}".
TaggedDatum     ::= identifier ":" quoted-string.

MembershipDecl  ::= ClassReferent.
ClassReferent   ::= "is" ClassID.

Rules           ::= Rule {"," Rule}.
Rule            ::= "to" StateReferent ["when" Expression].

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
        defns = []
        defns.append(self.defn())
        while self.scanner.consume(';'):
            defns.append(self.defn())
        if self.scanner.consume('begin'):
            # XXX read playfield
            pass
        else:
            self.scanner.expect('.')
        return AST('Alpaca', defns)

    def defn(self):
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
        if self.scanner.on('to'):
            r.append(self.rule())
            while self.scanner.consume(','):
                r.append(self.rule())
        return r

    def rule(self):
        self.scanner.expect('to')
        s = self.state_ref()
        e = AST('BoolLit', value='true')
        if self.scanner.consume('when'):
            e = self.expression()
        return AST('Rule', [s, e])

    def state_ref(self):
        if self.scanner.on_type('identifier'):
            id = self.scanner.consume_type('identifier')
            return AST('StateRefEq', value=id)
        elif self.scanner.on_type('arrow chain'):
            rel = self.scanner.consume_type('arrow chain')
            # XXX analyze rel to see if it is redundant
            return AST('StateRefRel', value=rel)
        self.scanner.expect('me')
        return AST('StateRefMe')

    def expression(self):
        e = self.term()
        while self.scanner.on_type('boolean operator'):
            op = self.scanner.consume_type('boolean operator')
            t = self.term()
            e = AST('BoolOp', [e, t], value=op)
        return e
    
    def term(self):
        if self.scanner.on_type('integer literal'):
            count = self.scanner.consume_type('integer literal')
            # XXX in neighbourhood
            if self.scanner.consume('is'):
                classid = self.scanner.consume_type('identifier')
                return AST('AdjacencyClass', value=classid)
            s = self.state_ref()
            return AST('Adjacency', [s], value=count)
        elif self.scanner.consume('('):
            e = self.expression()
            self.scanner.expect(')')
            return e
        elif self.scanner.consume('not'):
            e = self.term()
            return AST('Not', [e])
        elif self.scanner.on_type('boolean literal'):
            lit = self.scanner.consume_type('boolean literal')
            return AST('BoolLit', value=lit)
        else:
            s1 = self.state_ref()
            self.scanner.consume('=')  # optional
            if self.scanner.consume('is'):
                classid = self.scanner.consume_type('identifier')
                return AST('RelationalClass', [s1], value=classid)
            s2 = self.state_ref()
            return AST('Relational', [s2])
