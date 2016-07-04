@special
@rename("?")
def if_else(left, true_case, false_case):
    return true_case.eval() if left else false_case.eval()


@special
@rename("=>")
def define(left, right):
    globals()[right.value] = left
