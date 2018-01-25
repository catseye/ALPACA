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


def eval_relation(alpaca, playfield, x, y, state_id, ast, verbose=False):
    """state_id is the ID of a state (possibly from the playfield)
    that we want to check.  ast is either a StateRef or a ClassDecl.
    Returns true iff the state_id satisfies the StateRef or ClassDecl.

    """
    if ast.type == 'ClassDecl':
        class_id = ast.value
        state_ast = find_state_defn(alpaca, state_id)
        result = state_defn_is_a(alpaca, state_ast, class_id, verbose=verbose)
        if verbose:
            print " => checking if {} is_a {}: {}".format(state_id, class_id, result)
        return result
    elif ast.type in ('StateRefEq', 'StateRefRel'):
        pf_state_id = eval_state_ref(playfield, x, y, ast)
        return state_id == pf_state_id


def eval_expr(alpaca, playfield, x, y, ast, verbose=False):
    """Given a playfield and a position within it, and a boolean expression,
    return what the expression evaluates to at that position.
    
    """
    if ast.type == 'BoolOp':
        lhs = eval_expr(alpaca, playfield, x, y, ast.lhs, verbose=verbose)
        rhs = eval_expr(alpaca, playfield, x, y, ast.rhs, verbose=verbose)
        op = ast.value
        if op == 'and':
            return lhs and rhs
        elif op == 'or':
            return lhs or rhs
        elif op == 'xor':
            return lhs != rhs
    elif ast.type == 'Not':
        return not eval_expr(alpaca, playfield, x, y, ast.children[0], verbose=verbose)
    elif ast.type == 'Adjacency':
        rel = ast.lhs
        nb = ast.rhs
        if nb.type == 'NbhdRef':
            nb = find_nbhd_defn(alpaca, nb.value).children[0]
        assert nb.type == 'Neighbourhood'
        nb = set([node.value for node in nb.children])
        count = 0
        for (dx, dy) in nb:
            pf_state_id = playfield.get(x + dx, y + dy)
            if eval_relation(alpaca, playfield, x, y, pf_state_id, rel, verbose=verbose):
                count += 1
        #print "(%d,%d) has %d neighbours that are %r" % (x, y, count, rel)
        return count >= int(ast.value)
    elif ast.type == 'Relational':
        state_id = eval_state_ref(playfield, x, y, ast.lhs)
        rel = ast.rhs
        return eval_relation(alpaca, playfield, x, y, state_id, rel, verbose=verbose)
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


def eval_rules(alpaca, playfield, x, y, ast, verbose=False):
    """Given a playfield and a position within it, and a set of rules,
    return the "to" state for the rule that applies.

    If no rule applies, None is returned.

    """
    assert ast.type == 'Rules'
    for rule in ast.children:
        assert rule.type == 'Rule'
        s = rule.state_ref
        e = rule.expr
        if eval_expr(alpaca, playfield, x, y, e, verbose=verbose):
            return eval_state_ref(playfield, x, y, s)
    return None


# TODO: encapsulate this in an object to keep some state
# and reduce the number of recomputations each time
def evolve_playfield(playfield, new_pf, alpaca, verbose=False):
    if playfield.min_y is None:
        return
    bb = BoundingBox(0, 0, 0, 0)
    fit_bounding_box(alpaca, bb)
    y = playfield.min_y - bb.max_dy
    while y <= playfield.max_y - bb.min_dy:
        x = playfield.min_x - bb.max_dx
        while x <= playfield.max_x - bb.min_dx:
            state_id = playfield.get(x, y)
            if verbose:
                print "state at (%d,%d): %s" % (x, y, state_id)
            state_ast = find_state_defn(alpaca, state_id)
            if verbose:
                print " => %r" % state_ast
            classes = state_ast.classes
            rules = state_ast.rules
            new_state_id = apply_rules(alpaca, playfield, x, y, rules, classes, verbose=verbose)
            if new_state_id is None:
                new_state_id = state_id
            if verbose:
                print "new state: %s" % new_state_id
            new_pf.set(x, y, new_state_id)
            x += 1
        y += 1


def apply_rules(alpaca, playfield, x, y, rules, class_decls, verbose=False):
    """Given a set of rules and a set of superclasses (for a given state or
    class which is not given), try the rules; if none of them apply,
    recursively apply this function with the rules and superclasses for each
    given superclass.

    """
    new_state_id = eval_rules(alpaca, playfield, x, y, rules, verbose=verbose)
    if new_state_id is not None:
        return new_state_id
    assert class_decls.type == 'MembershipDecls'
    for class_decl in class_decls.children:
        assert class_decl.type == 'ClassDecl'
        class_id = class_decl.value
        class_ast = find_class_defn(alpaca, class_id)
        rules = class_ast.rules
        classes = class_ast.classes
        new_state_id = apply_rules(alpaca, playfield, x, y, rules, classes)        
        if new_state_id is not None:
            return new_state_id
    return None
