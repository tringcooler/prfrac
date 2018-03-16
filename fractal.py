
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
        def exp(self, val):
            return type(self)(val)
        if not '__expand__' in attrs:
            attrs['__expand__'] = exp
        for mn in meta_arith_ex.method_names:
            #mn = '__{:s}__'.format(mn)
            if mn in attrs:
                continue
            def mdst(mn):
                def _wrapper(self, *args, **kargs):
                    #print '_wrapper', mn
                    cls = type(self)
                    try:
                        smeth = getattr(super(cls, self), mn)
                    except:
                        return NotImplemented
                    r = smeth(*args, **kargs)
                    return self.__expand__(r)
                return _wrapper
            attrs[mn] = mdst(mn)
        return type.__new__(metaname, classname, baseclasses, attrs)

class float_ex(float):
    
    __metaclass__ = meta_arith_ex

    def __expand__(self, val):
        return type(self)(val, self.fractal)
    
    def __new__(cls, val, fractal):
        return super(float_ex, cls).__new__(cls, val)

    def __init__(self, val, fractal):
        super(float_ex, self).__init__(val)
        self.fractal = fractal
    

def _2list(val):
    if not hasattr(val, '__iter__'):
        return [val]
    else:
        return val

class fractal(object):

    def __init__(self):
        pass

    def __contains__(self, vals):
        vals = _2list(vals)
        groups = []
        for axis, val in enumerate(vals):
            if isinstance(val, float_ex):
                dst_frac = float_ex.fractal
                if (isinstance(dst_frac, sub_fractal)
                    and dst_frac.parent == self
                    and dst_frac.check_axis(axis)):
                    groups.append(axis)
                else:
                    return False
            else:
                return self.checkin(val)

    def __getitem__(self, rngs):
        rngs = _2list(rngs)
        for axis, rng in enumerate(rngs):
            if isinstance(rng, slice):
                if rng.step is None:
                    pass
                else:
                    pass
            else:
                pass

class sub_fractal(fractal):

    def __init__(self, parent, groups):
        super(sub_fractal, self).__init__()
        self.parent = parent
        self.groups = _2list(groups)

    def check_axis(self, axis):
        return axis in self.groups
