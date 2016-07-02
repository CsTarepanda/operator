#!/usr/bin/python3
import re
import ast
import pyfunc

pyfunc.update(globals())

def direct(*filenames):
    for filename in filenames:
        with open(filename + ("" if filename.endswith(".py") else ".py")) as f:
            exec(f.read(), globals())


class NoneValue: pass


class Value:
    def __init__(self, value):
        try:
            self.value = ast.literal_eval(value)
            self.literal = True
        except:
            self.value = value
            self.literal = False

    def eval(self):
        return self.value if self.literal else globals()[self.value]


direct("defines", "symbol_define", "special_define")

class Literal(Value):
    def __init__(self, value):
        self.value = value
        self.literal = True


class StringLiteral(Literal):
    def __init__(self, value):
        super().__init__(value)
        self.value = self.value.replace("\\\"", "\"")

    def __str__(self):
        return self.value

    def eval(self):
        return self.value


class NamelessFunction(Literal):
    def __init__(self, value):
        super().__init__(value)
        self.first_value, self.operator_ast = parse(self.value)
        self.literal = self.first_value == None

    def eval(self):
        return self.operator_ast if self.literal else eval(self.first_value, self.operator_ast)


literals = {
        "\"": StringLiteral,
        "(": NamelessFunction,
        }

end_literals = {
        StringLiteral: "\"",
        NamelessFunction: ")",
        }


def split_code_sub(code):
    return re.split(" +", code.strip())


def split_code(code):
    now = 0
    literal = None
    escape_flg = False
    spl = []
    literal_value = ""
    for index, i in enumerate(code):
        if (i in literals if literal == None else i == end_literals[literal]) and not escape_flg:
            if literal == None:
                literal = literals[i]
                if code[now:index]: spl += split_code_sub(code[now:index])
            else:
                spl.append(literal(literal_value))
                now = index + 1
                literal = None
                literal_value = ""
        elif literal != None:
            literal_value += i

        if i == "\\": escape_flg = True
        else: escape_flg = False
    if code[now:]: spl += split_code_sub(code[now:])

    return spl


def parse(code):
    code = code.strip()
    if re.match("^#[^#]", code):
        code = code[1:].strip()
    elif re.match("^##[^#]", code):
        code = "None " + code[2:].strip()
    else:
        return None
    operator_ast = list(create_ast(line_ast(split_code(code)), first_value=True))
    operator_ast[0] = operator_ast[0].eval()
    return tuple(operator_ast)

def create_ast(line_ast, first_value=False):
    if len(line_ast) <= 2: return tuple(line_ast)
    if first_value: return (line_ast[0][0], create_ast(line_ast[1:]))
    return tuple(line_ast[:2] + [create_ast(line_ast[2:])])

def line_ast(parse_code):
    result = []
    value = True
    values = []
    for i in parse_code:
        if value:
            values.append(i if isinstance(i, Value) else Value(i))
            value = False
        else:
            if i == ",":
                value = True
                continue
            else:
                result.append(tuple(values))
                values = []
                result.append(i)
                value = True
    if values: result.append(tuple(values))
    return result

@rename("->")
def eval(first_value, operator_ast):
    if operator_ast[0] in specials:
        value = globals()[operator_ast[0]](first_value, *operator_ast[1])
    else:
        value = globals()[operator_ast[0]](first_value, *[x.eval() for x in operator_ast[1]])
    if len(operator_ast) < 3:
        return value
    return eval(value, operator_ast[2])

print("\n=> %s" % eval(*parse(input(">> "))))
