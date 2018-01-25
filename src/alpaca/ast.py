# encoding: UTF-8

class AST(object):
    def __init__(self, **kwargs):
        self.attrs = kwargs
        for child in self.attrs.get('children', []):
            assert isinstance(child, AST), \
              "child %r of %r is not an AST node" % (child, self)        

    @property
    def type(self):
        return self.__class__.__name__

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.attrs)

    def __getattr__(self, name):
        if name in self.attrs:
            return self.attrs[name]
        raise AttributeError(name)

    def all_children(self):
        if 'children' in self.attrs:
            for child in self.children:
                yield child
        else:
            raise StopIteration


class Alpaca(AST):
    def __init__(self, defns=None, playfield=None):
        self.attrs = dict(defns=defns, playfield=playfield)

    def all_children(self):
        for defn in self.defns:
            for child in defn.all_children():
                yield child


class Neighbourhood(AST):
    pass

class StateRefRel(AST):
    pass

class Playfield(AST):
    pass

class CharRepr(AST):
    pass

class MembershipDecls(AST):
    pass

class StateDefn(AST):
    pass

class ClassDecl(AST):
    pass

class ClassDefn(AST):
    pass

class NbhdDefn(AST):
    pass

class Rules(AST):
    pass

class Rule(AST):
    pass

class StateRefEq(AST):
    pass

class StateRefRel(AST):
    pass

class NbhdRef(AST):
    pass

class Adjacency(AST):
    pass

class Relational(AST):
    pass

class Not(AST):
    pass

class BoolOp(AST):
    pass

class BoolLit(AST):
    pass
