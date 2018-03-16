
import numpy as np
from baker import baker_map, plot_histories

class meta_arith_ex(type):

    method_names = '''
        __add__ __sub__ __mul__ __floordiv__ __mod__ __divmod__
        __pow__ __lshift__ __rshift__ __and__ __xor__ __or__
        __div__ __truediv__ __radd__ __rsub__ __rmul__ __rdiv__
        __rtruediv__ __rfloordiv__ __rmod__ __rdivmod__ __rpow__
        __rlshift__ __rrshift__ __rand__ __rxor__ __ror__
        __iadd__ __isub__ __imul__ __idiv__ __itruediv__ __ifloordiv__
        __imod__ __ipow__ __ilshift__ __irshift__ __iand__ __ixor__
        __ior__ __neg__ __pos__ __abs__ __invert__
        '''.split() 
    
    def __new__(metaname, classname, baseclasses, attrs):
        for mn in meta_arith_ex.method_names:
            #mn = '__{:s}__'.format(mn)
            def mdst(mn):
                def _wrapper(self, *args, **kargs):
                    cls = type(self)
                    try:
                        smeth = getattr(super(cls, self), mn)
                    except:
                        return NotImplemented
                    r = smeth(*args, **kargs)
                    return cls(r)
                return _wrapper
            attrs[mn] = mdst(mn)
        return type.__new__(metaname, classname, baseclasses, attrs)

class float_ex(float):

    __metaclass__ = meta_arith_ex

class _float_ex(float):

    def __new__(self, val, exfunc):
        return super(float_ex, float_ex).__new__(float_ex, val)

    def __init__(self, val, exfunc):
        super(float_ex, self).__init__(val)
        self.exfunc = exfunc

    
