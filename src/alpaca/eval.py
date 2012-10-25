from alpaca.ast import AST


def eval_state_ref(playfield, x, y, ast):
    if ast.type == 'StateRefEq':
        return ast.value
    elif ast.type == 'StateRefRel':
        return playfield.get(x + ast.value[0], y + ast.value[1])
    else:
        raise NotImplementedError


def eval_expr(playfield, x, y, ast):
    """Given a playfield and a position within it, and a boolean expression,
    return what the expression evaluates to at that position.
    
    """
    if ast.type == 'BoolOp':
        lhs = eval_expr(playfield, x, y, ast.children[0])
        rhs = eval_expr(playfield, x, y, ast.children[1])
        if op == 'and':
            return lhs and rhs
        elif op == 'or':
            return lhs or rhs
        elif op == 'xor':
            return not (lhs == rhs)
    elif ast.type == 'Not':
        return not eval_expr(playfield, x, y, ast.children[0])
    elif ast.type == 'Adjacency':
        state = eval_state_ref(playfield, x, y, ast.children[0])
        #nb = ast.children[1]
        nb = set((0, -1), (-1, -1), (1, -1), (-1, 0), (1, 0), (0, 1), (-1, 1), (1, 1))
        for (dx, dy) in nb:
            if playfield.get(x + dx, y + dx) == state:
                count += 1
        return count >= int(ast.value)
    elif ast.type == 'Relational':
        raise NotImplementedError
    elif ast.type == 'BoolLit':
        if ast.value == 'true':
            return True
        elif ast.value == 'false':
            return False
        elif ast.value == 'guess':
            return False  # XXX randomly true or false
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError


def eval_state(playfield, x, y, ast):
    """Given a playfield and a position within it, and a boolean expression,
    return what the expression evaluates to at that position.
    
    """
    if ast.type == 'BoolOp':
        lhs = eval_expr(playfield, x, y, ast.children[0])
        rhs = eval_expr(playfield, x, y, ast.children[1])
        if op == 'and':
            return lhs and rhs
        elif op == 'or':
            return lhs or rhs
        elif op == 'xor':
            return not (lhs == rhs)
    elif ast.type == 'BoolLit':
        if ast.value == 'true':
            return True
        elif ast.value == 'false':
            return False
        elif ast.value == 'guess':
            return False  # XXX randomly true or false
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError
