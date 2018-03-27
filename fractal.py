
import numpy as np
from math import floor, frexp
from baker import baker_map, plot_histories

class meta_arith_ex(type):

    unary_op_method_names = '''
        __neg__ __pos__ __abs__ __invert__
        '''.split()

    binary_op_method_names = '''
        __add__ __sub__ __mul__ __floordiv__ __mod__ __divmod__
        __pow__ __lshift__ __rshift__ __and__ __xor__ __or__
        __div__ __truediv__ __radd__ __rsub__ __rmul__ __rdiv__
        __rtruediv__ __rfloordiv__ __rmod__ __rdivmod__ __rpow__
        __rlshift__ __rrshift__ __rand__ __rxor__ __ror__
        __iadd__ __isub__ __imul__ __idiv__ __itruediv__ __ifloordiv__
        __imod__ __ipow__ __ilshift__ __irshift__ __iand__ __ixor__
        __ior__
        '''.split()

    method_names = unary_op_method_names + binary_op_method_names
    
    def __new__(metaname, classname, baseclasses, attrs):
        base_cls = baseclasses[0]
        for mn in meta_arith_ex.method_names:
            if not hasattr(base_cls, mn):
                continue
            umeth = getattr(base_cls, mn)
            if mn in attrs:
                continue
            elif mn in meta_arith_ex.unary_op_method_names:
                def mdst1(m):
                    def _wrapper(self):
                        return self.__unop__(m)
                    return _wrapper
                attrs[mn] = mdst1(umeth)
            elif mn in meta_arith_ex.binary_op_method_names:
                def mdst2(m):
                    def _wrapper(self, val):
                        return self.__binop__(m, val)
                    return _wrapper
                attrs[mn] = mdst2(umeth)
        return type.__new__(metaname, classname, baseclasses, attrs)

from sys import float_info as _float_info

FCAP_MAX_PRECISION = _float_info.mant_dig

def highest_prec(val):
    m, e = frexp(val)
    return e

def prec_info(val):
    m, e = frexp(val)
    h = e
    l = e
    v = 0
    while not m.is_integer():
        m *= 2
        l -= 1
        v += 1
    return h, v, l

def mask_prec(val, lp):
    minf = 2 ** int(lp)
    return floor(val / minf) * minf

def minmax(*vals):
    sv = sorted(vals)
    return sv[0], sv[-1]

def is_divided(s, d, r = None):
    if r is None:
        r = s / d
    ms, es = frexp(s)
    md, ed = frexp(d)
    mr, er = frexp(r)
    bs = 2 ** FCAP_MAX_PRECISION
    si = int(ms * bs)
    di = int(md * bs)
    ri = int(mr * bs)
    rshft = int(53 + es - er - ed)
    rie = di * ri
    sie = (rie >> rshft)
    chb = (rie & ((1 << rshft) - 1))
    #print si, sie, chb, rie, rshft
    return si == sie and chb == 0

def _c_val_isin(val, loprec, fractal, context):
    vals = []
    axis = []
    for idx, itm in enumerate(context):
        if itm is None:
            itm = val
            axis.append(idx)
        vals.append(itm)
    info = fractal.check_val(*vals)
    ov = True
    eq = True
    rd = np.inf
    for idx in axis:
        if info[idx] is None:
            ov = False
            eq = False
            rd = 0
            break
        else:
            ieq, ird = info[idx]
            eq = (eq and ieq)
            rd = min(rd, ird)
    if rd is np.inf:
        rd = 0
    return ov, eq, rd

class float_ex(float):
    
    __metaclass__ = meta_arith_ex
    
    def __new__(cls, val, loprec):
        hiprec = highest_prec(val)
        if hiprec - loprec > FCAP_MAX_PRECISION:
            raise ValueError('float64 overflow.')
        val = mask_prec(val, loprec)
        return super(float_ex, cls).__new__(cls, val)

    def __init__(self, val, loprec):
        super(float_ex, self).__init__(val)
        self.raw = val
        self.loprec = loprec
        self.loprec_val = 2 ** loprec

    def __unop__(self, meth):
        v1 = meth(self.raw)
        v2 = meth(self.raw + self.loprec_val)
        return self.__expand__(*minmax(v1, v2))

    def __binop__(self, meth, val):
        if isinstance(val, float_ex):
            val_raw = val.raw
            val_lpv = val.loprec_val
        else:
            val_raw = val
            val_lpv = 2 ** (highest_prec(val) - FCAP_MAX_PRECISION)
        v1 = meth(self.raw, val_raw)
        v2 = meth(self.raw + self.loprec_val, val_raw)
        v3 = meth(self.raw, val_raw + val_lpv)
        v4 = meth(self.raw + self.loprec_val, val_raw + val_lpv)
        return self.__expand__(*minmax(v1, v2, v3, v4))

    def __expand__(self, vmin, vmax):
        
        return type(self)(val, self.fractal, self.context, loprec = maxrlp)
    

def _2list(val):
    if not hasattr(val, '__iter__'):
        return [val]
    else:
        return val

class fractal(object):

    def __init__(self):
        pass

    def check_val(self, *args):
        # not over: None
        # equal: True/False
        # reduce: int
        info = []
        for axis, val in enumerate(args):
            if True:
                if isinstance(val, float_ex):
                    info.append((False, 0))
                else:
                    #info.append((True, 0))
                    info.append((False, 0))
            else:
                info.append(None)
        return info

    def __contains__(self, vals):
        vals = _2list(vals)
        try:
            info = self.check_val(*vals)
        except:
            return False
        for r in info:
            if not r is None:
                return True
        else:
            return False

class baker_frac(fractal):

    def __init__(self, period, dprec = FEX_MAX_PRECISION):
        super(baker_frac, self).__init__()
        self.period = period
        self.dprec = dprec

    def check_val(self, x, y, t):
        pass



