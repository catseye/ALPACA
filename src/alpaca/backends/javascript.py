"""
Compile ALPACA AST to Javascript.

CURRENTLY JUST A STUB.

"""

class Compiler(object):
    def __init__(self, alpaca, file):
        """alpaca is an ALPACA description in AST form.  file is a file-like
        object to which the compiled code will be written.

        """
        self.alpaca = alpaca
        self.file = file

    def compile(self):
        self.file.write("""\
/*
 * This file was AUTOMATICALLY generated from an ALPACA description.
 * EDIT AT YOUR OWN RISK!
 */
""")
        defns = self.alpaca.children[0]
        for defn in defns.children:
            if defn.type == 'StateDefn':
                self.compile_state_defn(defn)
            elif defn.type == 'ClassDefn':
                pass
            elif defn.type == 'NbhdDefn':
                pass
            else:
                raise NotImplementedError(repr(defn))

    def compile_state_defn(self, defn):
        char_repr = defn.children[0]
        repr_decls = defn.children[1]
        membership = defn.children[2]
        rules = defn.children[3]
        self.file.write("function eval_%s(pf, x, y) {\n" % defn.value);
        for rule in rules.children:
            dest = rule.children[0]
            expr = rule.children[1]
            self.file.write("if (")
            self.compile_expr(expr)
            self.file.write(") {\n  return ")
            self.compile_state_ref(dest)
            self.file.write(";\n}\n" % (dest))
        self.file.write("return '%s';\n}\n\n" % defn.value)

    def compile_state_ref(self, ref):
        # compare to eval_state_ref
        if ref.type == 'StateRefEq':
            self.file.write("'%s'" % ref.value)
        elif ref.type == 'StateRefRel':
            self.file.write("pf.get(x+%d,y+%d)" % (ref.value[0], ref.value[1]))
        else:
            raise NotImplementedError(repr(expr))

    def compile_expr(self, expr):
        if expr.type == 'BoolOp':
            self.file.write('(')
            self.compile_expr(expr.children[0])
            self.file.write({
                'or': '||',
                'and': '&&',
                'xor': '!==',
            }[expr.value])
            self.compile_expr(expr.children[1])
            self.file.write(')')
        elif expr.type == 'Not':
            self.file.write('!(')
            self.compile_expr(expr.children[0])
            self.file.write(')')
        elif expr.type == 'BoolLit':
            self.file.write(expr.value)
        elif expr.type == 'Relational':
            # XXX todo: class membership
            self.file.write('(')
            self.compile_state_ref(expr.children[0])
            self.file.write('===')
            self.compile_state_ref(expr.children[1])
            self.file.write(')')
        elif expr.type == 'Adjacency':
            # XXX todo: class membership
            count = expr.value
            rel = expr.children[0]
            nb = expr.children[1]
            if nb.type == 'NbhdRef':
                nb = find_nbhd_defn(self.alpaca, nb.value).children[0]
            self.file.write('(in_nbhd(pf, x, y, ')
            self.compile_state_ref(rel)
            self.file.write(', [')
            self.file.write(','.join(
                ['[%d,%d]' % child.value for child in nb.children]
            ))
            self.file.write(']) >= %d)' % int(count))
        else:
            raise NotImplementedError(repr(expr))
