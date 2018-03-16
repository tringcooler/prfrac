
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
        def exp(self, val, mname):
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
                    return self.__expand__(r, mn, *args)
                return _wrapper
            attrs[mn] = mdst(mn)
        return type.__new__(metaname, classname, baseclasses, attrs)

FCAP_MAX_PRECISION = 50
FEX_MAX_PRECISION = 40

def highest_prec(val):
    return np.floor(np.log2(abs(val)))

def mask_prec(val, maxp, hp = None):
    if hp is None:
        hp = highest_prec(val)
    lp = hp - maxp + 1
    #minf = np.exp2(lp)
    minf = 2 ** int(lp)
    print lp, minf, np.floor(val / minf)
    return np.floor(val / minf) * minf

class float_ex(float):
    
    __metaclass__ = meta_arith_ex
    
    def __new__(cls, val, fractal, hiprec = None):
        return super(float_ex, cls).__new__(cls, val)

    def __init__(self, val, fractal, hiprec = None):
        super(float_ex, self).__init__(val)
        self.fractal = fractal
        if hiprec is None:
            hiprec = highest_prec(val)
        self.hiprec = hiprec

    def __expand__(self, val, mname, *args):
        _chk = lambda mn, lst: reduce(lambda r, v: r or v in mn, lst, False)
        def _hp(val):
            if hasattr(val, hiprec):
                return val.hiprec
            else:
                return highest_prec(val)
        shp = _hp(self)
        rhp = _hp(val)
        minhp = min(shp, rhp)
        maxhp = max(shp, rhp)
        _mm = lambda dhp: (min(minhp, dhp), max(maxhp, dhp))
        if _chk(mname, ['add', 'sub']):
            minhp, maxhp = _mm(_hp(arg[0]))
        elif _chk(mname, ['mul', 'div']):
            minhp, maxhp = _mm(_hp(arg[0]))
        if maxhp - minhp > FCAP_MAX_PRECISION - FEX_MAX_PRECISION:
            raise ValueError('float64 overflow.')
        return type(self)(val, self.fractal, rhp)

    def _fix_prec(self, val):
        pass
    

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
        for axis, val in enumerate(vals):
            if isinstance(val, float_ex):
                dst_frac = float_ex.fractal
                if not (isinstance(dst_frac, sub_fractal)
                    and dst_frac.parent == self
                    and axis in dst_frac.axis):
                    return False
            else:
                pass

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

    def __init__(self, parent, axis):
        super(sub_fractal, self).__init__()
        self.parent = parent
        self.axis = _2list(axis)

    def __eq__(self, dst):
        return self is dst or (isinstance(dst, sub_fractal)
            and self.parent == dst.parent
            and self.axis == dst.axis)

    def __neq__(self, dst):
        return not self == dst


