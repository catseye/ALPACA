from alpaca.ast import *
from alpaca.scanner import Scanner

"""
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
"""

NBHD_VON_NEUMANN = Neighbourhood(children=[
    StateRefRel(value=(0, -1)),
    StateRefRel(value=(0, 1)),
    StateRefRel(value=(-1, 0)),
    StateRefRel(value=(1, 0)),
])

NBHD_MOORE = Neighbourhood(children=[
    StateRefRel(value=(0, -1)),
    StateRefRel(value=(0, 1)),
    StateRefRel(value=(-1, 0)),
    StateRefRel(value=(-1, 1)),
    StateRefRel(value=(-1, -1)),
    StateRefRel(value=(1, 0)),
    StateRefRel(value=(1, 1)),
    StateRefRel(value=(1, -1)),
])

class Parser(object):
    def __init__(self, text):
        self.scanner = Scanner(text)

    def alpaca(self):
        defns = []
        defns.append(self.defn())
        pf = None
        while self.scanner.consume(';'):
            defns.append(self.defn())
        # we shan't consume() this token, lest the scanner jump
        # ahead assuming that the next token is normal.  If the
        # scanner is already on this token, the rest of the scanner
        # text is the playfield; so we just check on() here.
        if self.scanner.on('begin'):
            pf = self.scanner.scan_playfield()
        else:
            self.scanner.expect('.')
        playfield = Playfield(value=pf)
        return Alpaca(defns=defns, playfield=playfield)

    def defn(self):
        if self.scanner.on('state'):
            return self.state_defn()
        elif self.scanner.on('class'):
            return self.class_defn()
        elif self.scanner.on('neighbourhood'):
            return self.nbhd_defn()
        else:
            raise SyntaxError("Expected 'state', 'class', or "
                              "'neighbourhood', but found "
                              "'%s'" % self.scanner.token)
    
    def state_defn(self):
        self.scanner.expect('state')
        id = self.scanner.consume_type('identifier')
        attrs = []
        char_repr = CharRepr(value=self.scanner.consume_type('string literal'))
        classes = []
        while self.scanner.on('is'):
            classes.append(self.class_decl())
        rules = self.rules()
        return StateDefn(id=id, char_repr=char_repr, classes=classes, rules=rules)

    def class_decl(self):
        self.scanner.expect('is')
        id = self.scanner.consume_type('identifier')
        return ClassDecl(id=id)

    def class_defn(self):
        self.scanner.expect('class')
        id = self.scanner.consume_type('identifier')
        classes = []
        while self.scanner.on('is'):
            classes.append(self.class_decl())
        rules = self.rules()
        return ClassDefn(id=id, rules=rules, classes=classes)

    def nbhd_defn(self):
        self.scanner.expect('neighbourhood')
        self.scanner.check_type('identifier')
        id = self.scanner.consume_type('identifier')
        n = self.neighbourhood()
        return NbhdDefn(id=id, children=[n])

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
        e = BoolLit(value='true')
        if self.scanner.consume('when'):
            e = self.expression()
        return Rule(state_ref=s, expr=e)

    def state_ref(self):
        if self.scanner.on_type('identifier'):
            id = self.scanner.consume_type('identifier')
            return StateRefEq(id=id)
        elif self.scanner.on_type('arrow chain'):
            rel = self.scanner.consume_type('arrow chain')
            (dx, dy) = resolve_arrow_chain(rel)
            return StateRefRel(value=(dx, dy))
        self.scanner.expect('me')
        return StateRefRel(value=(0, 0))

    def neighbourhood(self):
        self.scanner.expect('(')
        refs = []
        while self.scanner.on_type('arrow chain'):
            refs.append(self.state_ref())
        self.scanner.expect(')')
        return Neighbourhood(children=refs)

    def expression(self):
        e = self.term()
        while self.scanner.on_type('boolean operator'):
            op = self.scanner.consume_type('boolean operator')
            t = self.term()
            e = BoolOp(lhs=e, rhs=t, op=op)
        return e
    
    def term(self):
        if self.scanner.on_type('integer literal'):
            count = self.scanner.consume_type('integer literal')
            nbhd = NBHD_MOORE
            if self.scanner.consume('in'):
                if self.scanner.on_type('identifier'):
                    id = self.scanner.consume_type('identifier')
                    nbhd = NbhdRef(id=id)
                else:
                    nbhd = self.neighbourhood()
            if self.scanner.on('is'):
                rel = self.class_decl()
            else:
                rel = self.state_ref()
            return Adjacency(rel=rel, nbhd=nbhd, count=count)
        elif self.scanner.consume('('):
            e = self.expression()
            self.scanner.expect(')')
            return e
        elif self.scanner.consume('not'):
            e = self.term()
            return Not(expr=e)
        elif self.scanner.on_type('boolean literal'):
            lit = self.scanner.consume_type('boolean literal')
            return BoolLit(value=lit)
        else:
            sr = self.state_ref()
            if self.scanner.on('is'):
                rel = self.class_decl()
            else:
                self.scanner.consume('=')  # optional
                rel = self.state_ref()
            return Relational(lhs=sr, rhs=rel)


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
