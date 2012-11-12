"""
Backend for compiling ALPACA AST to Javascript.  Not yet complete.

"""

from alpaca.analysis import get_class_map, find_nbhd_defn


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
        class_map = get_class_map(self.alpaca)
        for (class_id, state_set) in class_map.iteritems():
            self.file.write("function is_%s(st) {\n" % class_id)
            self.file.write("  return ");
            for state_id in state_set:
                self.file.write("(st === '%s') || " % state_id)
            self.file.write("0;\n}\n\n")
        defns = self.alpaca.children[0]
        for defn in defns.children:
            if defn.type == 'ClassDefn':
                self.compile_class_defn(defn)
        for defn in defns.children:
            if defn.type == 'StateDefn':
                self.compile_state_defn(defn)

    def compile_class_defn(self, defn):
        membership = defn.children[1]
        rules = defn.children[0]
        self.file.write("function evalClass_%s(pf, x, y) {\nvar id;\n" % defn.value);
        for rule in rules.children:
            dest = rule.children[0]
            expr = rule.children[1]
            self.file.write("if (")
            self.compile_expr(expr)
            self.file.write(") {\n  return ")
            self.compile_state_ref(dest)
            self.file.write(";\n}\n" % (dest))
        for superclass in membership.children:
            self.file.write("id = evalClass_%s(pf, x, y);\n" % superclass.value)
            self.file.write("if (id !=== undefined) return id;\n")
        self.file.write("return undefined;\n}\n\n")

    def compile_state_defn(self, defn):
        #char_repr = defn.children[0]
        #repr_decls = defn.children[1]
        membership = defn.children[2]
        rules = defn.children[3]
        self.file.write("function eval_%s(pf, x, y) {\nvar id;\n" % defn.value);
        for rule in rules.children:
            dest = rule.children[0]
            expr = rule.children[1]
            self.file.write("if (")
            self.compile_expr(expr)
            self.file.write(") {\n  return ")
            self.compile_state_ref(dest)
            self.file.write(";\n}\n" % (dest))
        for superclass in membership.children:
            self.file.write("id = evalClass_%s(pf, x, y);\n" % superclass.value)
            self.file.write("if (id !=== undefined) return id;\n")
        self.file.write("return '%s';\n}\n\n" % defn.value)

    def compile_state_ref(self, ref):
        # compare to eval_state_ref
        if ref.type == 'StateRefEq':
            self.file.write("'%s'" % ref.value)
        elif ref.type == 'StateRefRel':
            self.file.write("pf.get(x+%d,y+%d)" % (ref.value[0], ref.value[1]))
        else:
            raise NotImplementedError(repr(ref))

    def compile_relation(self, ref, ast):
        if ast.type == 'ClassDecl':
            self.file.write('is_%s(' % ast.value)
            self.compile_state_ref(ref)
            self.file.write(")")
        else:
            self.file.write('(')
            self.compile_state_ref(ref)
            self.file.write('===')
            self.compile_state_ref(ast)
            self.file.write(')')

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
            self.compile_relation(expr.children[0], expr.children[1])
        elif expr.type == 'Adjacency':
            count = expr.value
            rel = expr.children[0]
            nb = expr.children[1]
            if nb.type == 'NbhdRef':
                nb = find_nbhd_defn(self.alpaca, nb.value).children[0]
            if rel.type == 'ClassDecl':
                self.file.write("(in_nbhd_pred(pf, x, y, is_%s" % rel.value)
            else:
                self.file.write('(in_nbhd_eq(pf, x, y, ')
                self.compile_state_ref(rel)
            self.file.write(', [')
            self.file.write(','.join(
                ['[%d,%d]' % child.value for child in nb.children]
            ))
            self.file.write(']) >= %d)' % int(count))
        else:
            raise NotImplementedError(repr(expr))
