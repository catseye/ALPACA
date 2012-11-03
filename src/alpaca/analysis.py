"""
Functions for discovering certain things about an ALPACA description
given its AST.

"""

from alpaca.ast import AST
from alpaca.playfield import Playfield


def get_defns(alpaca):
    assert alpaca.type == 'Alpaca'
    defns = alpaca.children[0]
    assert defns.type == 'Defns'
    return defns


def find_defn(alpaca, type, id):
    assert isinstance(id, basestring)
    for defn in get_defns(alpaca).children:
        if defn.type == type and defn.value == id:
            return defn
    raise KeyError, "No such %s '%s'" % (type, id)
  

def find_state_defn(alpaca, state_id):
    return find_defn(alpaca, 'StateDefn', state_id)


def find_class_defn(alpaca, class_id):
    return find_defn(alpaca, 'ClassDefn', class_id)


def state_defn_is_a(alpaca, state_ast, class_id):
    class_decls = state_ast.children[2]
    assert class_decls.type == 'MembershipDecls'
    for class_decl in class_decls.children:
        assert class_decl.type == 'ClassDecl'
        if class_id == class_decl.value:
            return True
        class_ast = find_class_defn(alpaca, class_id)
        if class_defn_is_a(alpaca, class_ast, class_id):
            return True
    return False


def class_defn_is_a(alpaca, class_ast, class_id):
    if class_ast.value == class_id:
        return True
    class_decls = class_ast.children[1]
    assert class_decls.type == 'MembershipDecls'
    for class_decl in class_decls.children:
        assert class_decl.type == 'ClassDecl'
        if class_id == class_decl.value:
            return True
        parent_class_ast = find_class_defn(alpaca, class_id)
        if class_defn_is_a(alpaca, parent_class_ast, class_id):
            return True
    return False


def construct_representation_map(alpaca):
    map = {}
    for defn in get_defns(alpaca).children:
        if defn.type == 'StateDefn':
            repr = defn.children[0]
            assert repr.type == 'CharRepr'
            map[repr.value] = defn.value
    return map


def get_default_state(alpaca):
    for defn in get_defns(alpaca).children:
        if defn.type == 'StateDefn':
            return defn.value


def get_defined_playfield(alpaca):
    assert alpaca.type == 'Alpaca'
    playast = alpaca.children[1]
    assert playast.type == 'Playfield'
    if playast.value is None:
        return None
    repr_map = construct_representation_map(alpaca)
    pf = Playfield(get_default_state(alpaca), repr_map)
    for (x, y, ch) in playast.value:
        pf.set(x, y, repr_map[ch])
    pf.recalculate_limits()
    return pf
