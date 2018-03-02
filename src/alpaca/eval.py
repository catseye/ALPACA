"""
Direct evaluator of ALPACA AST nodes.

"""

from alpaca.analysis import (
    find_state_defn, find_class_defn, find_nbhd_defn, state_defn_is_a,
    BoundingBox, fit_bounding_box,
)

import random

def eval_state_ref(playfield, x, y, ast):
    if ast.type == 'StateRefEq':
        return ast.value
    elif ast.type == 'StateRefRel':
        return playfield.get(x + ast.value[0], y + ast.value[1])
    else:
        raise NotImplementedError


def eval_relation(alpaca, playfield, x, y, state_id, ast):
    """state_id is the ID of a state (possibly from the playfield)
    that we want to check.  ast is either a StateRef or a ClassDecl.
    Returns true iff the state_id satisfies the StateRef or ClassDecl.

    """
    if ast.type == 'ClassDecl':
        class_id = ast.value
        state_ast = find_state_defn(alpaca, state_id)
        return state_defn_is_a(alpaca, state_ast, class_id)
    elif ast.type in ('StateRefEq', 'StateRefRel'):
        pf_state_id = eval_state_ref(playfield, x, y, ast)
        return state_id == pf_state_id


def eval_expr(alpaca, playfield, x, y, ast):
    """Given a playfield and a position within it, and a boolean expression,
    return what the expression evaluates to at that position.
    
    """
    if ast.type == 'BoolOp':
        lhs = eval_expr(alpaca, playfield, x, y, ast.children[0])
        rhs = eval_expr(alpaca, playfield, x, y, ast.children[1])
        op = ast.value
        if op == 'and':
            return lhs and rhs
        elif op == 'or':
            return lhs or rhs
        elif op == 'xor':
            return lhs != rhs
    elif ast.type == 'Not':
        return not eval_expr(alpaca, playfield, x, y, ast.children[0])
    elif ast.type == 'Adjacency':
        rel = ast.children[0]
        nb = ast.children[1]
        if nb.type == 'NbhdRef':
            nb = find_nbhd_defn(alpaca, nb.value).children[0]
        assert nb.type == 'Neighbourhood'
        nb = set([node.value for node in nb.children])
        count = 0
        for (dx, dy) in nb:
            pf_state_id = playfield.get(x + dx, y + dy)
            if eval_relation(alpaca, playfield, x, y, pf_state_id, rel):
                count += 1
        #print "(%d,%d) has %d neighbours that are %r" % (x, y, count, rel)
        return count >= int(ast.value)
    elif ast.type == 'Relational':
        state_id = eval_state_ref(playfield, x, y, ast.children[0])
        rel = ast.children[1]
        return eval_relation(alpaca, playfield, x, y, state_id, rel)
    elif ast.type == 'BoolLit':
        if ast.value == 'true':
            return True
        elif ast.value == 'false':
            return False
        elif ast.value == 'guess':
            return bool(random.getrandbits(1))
        else:
            raise NotImplementedError(repr(ast))
    else:
        raise NotImplementedError(repr(ast))


def eval_rules(alpaca, playfield, x, y, ast):
    """Given a playfield and a position within it, and a set of rules,
    return the "to" state for the rule that applies.

    If no rule applies, None is returned.

    """
    assert ast.type == 'Rules'
    for rule in ast.children:
        assert rule.type == 'Rule'
        s = rule.children[0]
        e = rule.children[1]
        if eval_expr(alpaca, playfield, x, y, e):
            return eval_state_ref(playfield, x, y, s)
    return None


# TODO: encapsulate this in an object to keep some state
# and reduce the number of recomputations each time
def evolve_playfield(playfield, new_pf, alpaca):
    if playfield.min_y is None:
        return
    bb = BoundingBox(0, 0, 0, 0)
    fit_bounding_box(alpaca, bb)
    y = playfield.min_y - bb.max_dy
    while y <= playfield.max_y - bb.min_dy:
        x = playfield.min_x - bb.max_dx
        while x <= playfield.max_x - bb.min_dx:
            state_id = playfield.get(x, y)
            #print "state at (%d,%d): %s" % (x, y, state_id)
            state_ast = find_state_defn(alpaca, state_id)
            #print " => %r" % state_ast
            classes = state_ast.children[2]
            rules = state_ast.children[3]
            new_state_id = apply_rules(alpaca, playfield, x, y, rules, classes)
            if new_state_id is None:
                new_state_id = state_id
            #print "new state: %s" % new_state_id
            new_pf.set(x, y, new_state_id)
            x += 1
        y += 1


def apply_rules(alpaca, playfield, x, y, rules, class_decls, checked_classes=[]):
    """Given a set of rules and a set of superclasses (for a given state or
    class which is not given), try the rules; if none of them apply,
    recursively apply this function with the rules and superclasses for each
    given superclass.

    """
    new_state_id = eval_rules(alpaca, playfield, x, y, rules)
    if new_state_id is not None:
        return new_state_id
    assert class_decls.type == 'MembershipDecls'
    for class_decl in class_decls.children:
        assert class_decl.type == 'ClassDecl'
        class_id = class_decl.value
        if class_id in checked_classes:
            continue
        class_ast = find_class_defn(alpaca, class_id)
        rules = class_ast.children[0]
        classes = class_ast.children[1]
        checked_classes.append(class_id)
        new_state_id = apply_rules(alpaca, playfield, x, y, rules, classes, checked_classes)
        if new_state_id is not None:
            return new_state_id
    return None
