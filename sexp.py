import string
import StringIO
import sys
import types

PAREN = 0
STRING = 1


class ParseError(Exception):
    pass


def parse(s):
    if isinstance(s, types.StringType):
        return parse(StringIO.StringIO(s))

    return Sexp(parse_(s, [], []))

def parse_(s, stack, results):
    while True:
        if len(stack) == 0 or stack[0] == PAREN:
            c = None
            while True:
                c = s.read(1)
                if c == '':
                    return results[0]
                if c not in string.whitespace:
                    break
            if c == '"':
                stack = [STRING] + stack
                results = [""] + results
            elif c == '(':
                stack = [PAREN] + stack
                results = [[]] + results
            elif c == ')':
                stack = stack[1:]
                top = results[0]
                results = results[1:]
                if stack == []:
                    return top
                else:
                    results[0].append(top)
            else:
                raise ParseError()
        elif stack[0] == STRING:
            c = s.read(1)
            if c == '"':
                stack = stack[1:]
                top = results[0]
                results = results[1:]
                results[0].append(top)
            elif c == '\\':
                c = s.read(1)
                results[0] += c
            elif c == '':
                raise ParseError()
            else:
                results[0] += c
        else:
            raise ParseError()


class Sexp:
    def __init__(self, val):
        self.val = val


    def car(self):
        return Sexp(self.val[0])


    def cdr(self):
        return Sexp(self.val[1:])


    def assoc(self, key):
        for v in self.val:
            if len(v) > 1 and v[0] == key:
                return Sexp(v[1])

    def set_assoc(self, key, new_val):
        for v in self.val:
            if len(v) > 1 and v[0] == key:
                v[1] = new_val

    def toString(self):
        io = StringIO.StringIO()
        try:
            self.toString_(io, self.val)
            io.seek(0)
            return io.getvalue()
        finally:
            io.close()


    def toString_(self, io, v):
        if isinstance(v, types.ListType):
            space = False
            io.write('(')
            for x in v:
                if space:
                    io.write(' ')
                self.toString_(io, x)
                space = True
            io.write(')')
        else:
            io.write('"' + v.replace('"', '\"') + '"')


if __name__ == "__main__":
    try:
        sexp = parse('((()))')
        print str(sexp.val)
        print sexp.toString()
        sexp = parse('("X" "Y")')
        print str(sexp.val)
        print sexp.toString()
        sexp = parse('(("foo" "(\\""))')
        print str(sexp.val)
        print sexp.toString()
        sexp = parse('(("location" "//samba/foo") ("username" "foo") ("cifspassword" "hello") ("options" "-t cifs "))')
        print str(sexp.val)
        print sexp.toString()
        print sexp.car().toString()
        print sexp.cdr().toString()
        print sexp.assoc('cifspassword').toString()
        sexp.set_assoc('cifspassword', 'REMOVED')
        print sexp.toString()
        sys.exit(0)
    except KeyboardInterrupt:
        print "\nInterrupted."
        sys.exit(1)
