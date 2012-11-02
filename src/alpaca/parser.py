from alpaca.ast import AST
from alpaca.scanner import Scanner

"""
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
"""

NBHD_VON_NEUMANN = AST('Neighbourhood', [
    AST('StateRefRel', value=(0, -1)),
    AST('StateRefRel', value=(0, 1)),
    AST('StateRefRel', value=(-1, 0)),
    AST('StateRefRel', value=(1, 0))
])

NBHD_MOORE = AST('Neighbourhood', [
    AST('StateRefRel', value=(0, -1)),
    AST('StateRefRel', value=(0, 1)),
    AST('StateRefRel', value=(-1, 0)),
    AST('StateRefRel', value=(-1, 1)),
    AST('StateRefRel', value=(-1, -1)),
    AST('StateRefRel', value=(1, 0)),
    AST('StateRefRel', value=(1, 1)),
    AST('StateRefRel', value=(1, -1)),
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
        playfield = AST('Playfield', value=pf)
        return AST('Alpaca', [AST('Defns', defns), playfield])

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
        char_repr = AST('CharRepr',
                        value=self.scanner.consume_type('string literal'))
        if self.scanner.consume('{'):
            attrs.append(self.attribute())
            while self.scanner.consume(','):
                attrs.append(self.attribute())
            self.scanner.expect('}')
        attrs = AST('ReprDecls', attrs)
        classes = []
        while self.scanner.on('is'):
            classes.append(self.class_decl())
        classes = AST('MembershipDecls', classes)
        rules = self.rules()
        return AST('StateDefn', [char_repr, attrs, classes, rules],
                   value=id)

    def attribute(self):
        id = self.scanner.consume_type('identifier')
        self.scanner.expect(':')
        value = self.scanner.consume_type('string literal')
        return AST('Attribute', value=(id, value))

    def class_decl(self):
        self.scanner.expect('is')
        id = self.scanner.consume_type('identifier')
        return AST('ClassDecl', value=id)

    def class_defn(self):
        self.scanner.expect('class')
        id = self.scanner.consume_type('identifier')
        classes = []
        while self.scanner.on('is'):
            classes.append(self.class_decl())
        classes = AST('MembershipDecls', classes)
        rules = self.rules()
        return AST('ClassDefn', [rules, classes], value=id)

    def nbhd_defn(self):
        self.scanner.expect('neighbourhood')
        self.scanner.check_type('identifier')
        id = self.scanner.consume_type('identifier')
        n = self.neighbourhood()
        return AST('NbhdDefn', [n], value=id)

    def rules(self):
        r = []
        if self.scanner.on('to'):
            r.append(self.rule())
            while self.scanner.consume(','):
                r.append(self.rule())
        return AST('Rules', r)

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

    def neighbourhood(self):
        self.scanner.expect('(')
        refs = []
        while self.scanner.on_type('arrow chain'):
            refs.append(self.state_ref())
        self.scanner.expect(')')
        return AST('Neighbourhood', refs)

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
            nb = NBHD_MOORE
            if self.scanner.consume('in'):
                if self.scanner.on_type('identifier'):
                    nb = AST('NbhdRef',
                             value=self.scanner.consume_type('identifier'))
                else:
                    nb = self.neighbourhood()
            if self.scanner.on('is'):
                rel = self.class_decl()
            else:
                rel = self.state_ref()
            return AST('Adjacency', [rel, nb], value=count)
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
            sr = self.state_ref()
            if self.scanner.on('is'):
                rel = self.class_decl()
            else:
                self.scanner.consume('=')  # optional
                rel = self.state_ref()
            return AST('Relational', [sr, rel])


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
