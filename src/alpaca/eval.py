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
        return ast.id
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
        class_id = ast.id
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
        op = ast.op
        if op == 'and':
            return lhs and rhs
        elif op == 'or':
            return lhs or rhs
        elif op == 'xor':
            return lhs != rhs
    elif ast.type == 'Not':
        return not eval_expr(alpaca, playfield, x, y, ast.expr, verbose=verbose)
    elif ast.type == 'Adjacency':
        rel = ast.rel
        nbhd = ast.nbhd
        if nbhd.type == 'NbhdRef':
            nbhd = find_nbhd_defn(alpaca, nbhd.id).children[0]
        assert nbhd.type == 'Neighbourhood'
        count = 0
        for (dx, dy) in set([node.value for node in nbhd.children]):
            pf_state_id = playfield.get(x + dx, y + dy)
            if eval_relation(alpaca, playfield, x, y, pf_state_id, rel, verbose=verbose):
                count += 1
        #print "(%d,%d) has %d neighbours that are %r" % (x, y, count, rel)
        return count >= int(ast.count)
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


def eval_rules(alpaca, playfield, x, y, rules, verbose=False):
    """Given a playfield and a position within it, and a set of rules,
    return the "to" state for the rule that applies.

    If no rule applies, None is returned.

    """
    for rule in rules:
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


def apply_rules(alpaca, playfield, x, y, rules, class_decls, checked_classes=None, verbose=False):
    """Given a set of rules and a set of superclasses (for a given state or
    class which is not given), try the rules; if none of them apply,
    recursively apply this function with the rules and superclasses for each
    given superclass.

    """
    if checked_classes is None:
        checked_classes = set()
    new_state_id = eval_rules(alpaca, playfield, x, y, rules, verbose=verbose)
    if new_state_id is not None:
        return new_state_id
    for class_decl in class_decls:
        assert class_decl.type == 'ClassDecl'
        class_id = class_decl.id
        if class_id in checked_classes:
            continue
        class_ast = find_class_defn(alpaca, class_id)
        rules = class_ast.rules
        classes = class_ast.classes
        checked_classes.add(class_id)
        new_state_id = apply_rules(
            alpaca, playfield, x, y, rules, classes,
            checked_classes=checked_classes, verbose=verbose
        )
        if new_state_id is not None:
            return new_state_id
    return None
