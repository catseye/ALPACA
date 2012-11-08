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


def find_nbhd_defn(alpaca, nbhd_id):
    return find_defn(alpaca, 'NbhdDefn', nbhd_id)


def state_defn_is_a(alpaca, state_ast, class_id):
    class_decls = state_ast.children[2]
    assert class_decls.type == 'MembershipDecls'
    for class_decl in class_decls.children:
        assert class_decl.type == 'ClassDecl'
        if class_id == class_decl.value:
            return True
        class_ast = find_class_defn(alpaca, class_decl.value)
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


class BoundingBox(object):
    def __init__(self, min_dx, min_dy, max_dx, max_dy):
        self.min_dx = min_dx
        self.min_dy = min_dy
        self.max_dx = max_dx
        self.max_dy = max_dy

    def expand_to_contain(self, dx, dy):
        if dx < self.min_dx:
            self.min_dx = dx
        if dx > self.max_dx:
            self.max_dx = dx
        if dy < self.min_dy:
            self.min_dy = dy
        if dy > self.max_dy:
            self.max_dy = dy

    def __repr__(self):
        return "BoundingBox(%d, %d, %d, %d)" % (
            self.min_dx, self.min_dy, self.max_dx, self.max_dy
        )


def fit_bounding_box(ast, bb):
    """Given an ALPACA AST, expand the given bounding box to
    encompass all relative references used within th AST.

    """
    if ast.type == 'StateRefRel':
        (dx, dy) = ast.value
        bb.expand_to_contain(dx, dy)
    for child in ast.children:
        fit_bounding_box(child, bb=bb)
