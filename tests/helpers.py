import sys
from types import FunctionType


py3 = sys.version_info.major >= 3


def undecorate(fn):
    """
    Return undecorated function. The implementation is based on (well...
    copied) `from Bottle <http://bit.ly/1TeOrjn>`_.
    """
    fn = getattr(fn, '__func__' if py3 else 'im_func', fn)
    closure_attr = '__closure__' if py3 else 'func_closure'
    while hasattr(fn, closure_attr) and getattr(fn, closure_attr):
        attributes = getattr(fn, closure_attr)
        fn = attributes[0].cell_contents

        # in case of decorators with multiple arguments
        if not isinstance(fn, FunctionType):
            # pick first FunctionType instance from multiple arguments
            fn = filter(lambda x: isinstance(x, FunctionType),
                        map(lambda x: x.cell_contents, attributes))
            fn = list(fn)[0]  # py3 support
    return fn
