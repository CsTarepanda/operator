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
        return globals()[self.value] if self.literal else self.value


direct("defines", "symbol_define")


def split_code(code):
    return re.split(" ", code)


def parse(code):
    if re.match("^#[^#]", code):
        code = code[1:].strip()
        return create_ast(line_ast(split_code(code)), first_value=True)
    elif re.match("^##[^#]", code):
        code = "None " + code[2:].strip()
        return create_ast(line_ast(split_code(code)), first_value=True)
    else:
        return None

def literal_or_string(value):
    try:
        return ast.literal_eval(value)
    except:
        return value

def create_ast(line_ast, first_value=False):
    if len(line_ast) <= 2: return tuple(line_ast)
    if first_value: return (line_ast[0][0], create_ast(line_ast[1:]))
    return tuple(line_ast[:2] + [create_ast(line_ast[2:])])

def line_ast(parse_code):
    result = []
    value = True
    values = []
    # for i in [Value(x) for x in parse_code]:
    for i in parse_code:
        if value:
            values.append(Value(i))
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

def eval(first_value, operator_ast):
    value = globals()[operator_ast[0]](first_value.eval(), *[x.eval() for x in operator_ast[1]])
    if len(operator_ast) < 3:
        return value
    return eval(value, operator_ast[2])

code = "#6 * 2 , 3 |> int |> print"
code = "##print $> 10 == None ? 30 , 40"
ev = eval(*parse(code))
print(ev)
# print(eval(*parse(code)))

# ev = eval(*parse(code))

# print(eval(eval(*parse(code))))
