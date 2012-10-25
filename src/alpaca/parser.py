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
        playfield = None
        defns.append(self.defn())
        while self.scanner.consume(';'):
            defns.append(self.defn())
        if self.scanner.consume('begin'):
            playfield = self.scanner.read_playfield()
        else:
            self.scanner.expect('.')
        return AST('Alpaca', [defns, playfield])

    def defn(self):
        if self.scanner.on('state'):
            return self.state_defn()
        elif self.scanner.on('class'):
            return self.class_defn()
        elif self.scanner.on('neighbourhood'):
            return self.neighbourhood_defn()
        else:
            raise SyntaxError("Expected 'state', 'class', or "
                              "'neighbourhood', but found "
                              "'%s'" % self.scanner.token)
    
    def state_defn(self):
        self.scanner.expect('state')
        id = self.scanner.consume_type('identifier')
        attrs = []
        char_repr = self.scanner.consume_type('string literal')
        if self.scanner.consume('{'):
            attrs.append(self.tagged_datum())
            while self.scanner.consume(','):
                attrs.append(self.tagged_datum())
            self.scanner.expect('}')
        classes = []
        while self.scanner.consume('is'):
            classes.append(self.scanner.consume_type('identifier'))
        rules = self.rules()
        return AST('StateDefn', [char_repr, attrs, classes, rules],
                   value=id)

    def tagged_datum(self):
        id = self.scanner.consume_type('identifier')
        self.scanner.expect(':')
        value = self.scanner.consume_type('string literal')
        return AST('Attribute', [id, value])

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
            (dx, dy) = resolve_arrow_chain(rel)
            return AST('StateRefRel', value=(dx, dy))
        self.scanner.expect('me')
        return AST('StateRefRel', value=(0, 0))

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
            nb = None  # XXX default Moore neighbourhood
            if self.scanner.consume('in'):
                if self.scanner.on_type('identifier'):
                    nb = self.scanner.consume('identifier')
                else:
                    nb = self.neighbourhood()
            if self.scanner.consume('is'):
                classid = self.scanner.consume_type('identifier')
                return AST('AdjacencyClass', value=classid)
            s = self.state_ref()
            return AST('Adjacency', [s, nb], value=count)
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


def resolve_arrow_chain(s):
    dx = 0
    dy = 0
    for c in s:
        if c == '<':
            dx -= 1
        elif c == '>':
            dx += 1
        elif c == '^':
            dy -= 1
        elif c == 'v':
            dy += 1
        else:
            raise ValueError
    # XXX produce warning if the len of s is longer than
    # is necessary to get dx, dy
    return (dx, dy)
