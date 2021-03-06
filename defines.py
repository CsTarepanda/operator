specials = {}


def rename(name):
    def deco(fnc):
        fnc.__name__ = name
        globals()[name] = fnc
        return fnc
    return deco


def special(fnc):
    specials[fnc.__name__] = fnc
    return fnc
