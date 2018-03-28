
import numpy as np
from math import floor, frexp
from random import random

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
inf = float('inf')

def highest_prec(val):
    m, e = frexp(val)
    return e

def default_lowest_prec(val):
    return highest_prec(val) - FCAP_MAX_PRECISION

def prec2val(p):
    if p == inf:
        return inf
    elif p == -inf:
        return 0
    else:
        return 2 ** int(p)

def mask_prec(val, lp):
    minf = prec2val(lp)
    return floor(val / minf) * minf

def minmax(*vals):
    sv = sorted(vals)
    return sv[0], sv[-1]

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

class float_ex(float):
    
    __metaclass__ = meta_arith_ex
    
    def __new__(cls, val, loprec = None):
        hiprec = highest_prec(val)
        if loprec is None:
            loprec = -inf
        elif not loprec == -inf:
            loprec = max(loprec, hiprec - FCAP_MAX_PRECISION)
            val = mask_prec(val, loprec)
        inst = super(float_ex, cls).__new__(cls, val)
        inst.raw = val
        inst.loprec = loprec
        inst.loprec_val = prec2val(loprec)
        return inst

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
            val_lpv = 0
        v1 = meth(self.raw, val_raw)
        v2 = meth(self.raw + self.loprec_val, val_raw)
        v3 = meth(self.raw, val_raw + val_lpv)
        v4 = meth(self.raw + self.loprec_val, val_raw + val_lpv)
        return self.__expand__(*minmax(v1, v2, v3, v4))

    def __expand__(self, vmin, vmax):
        vdlt = vmax - vmin
        vdlt -= prec2val(default_lowest_prec(vdlt))
        return type(self)(vmin, highest_prec(vdlt))

    def mask(self, hiprec = None, loprec = None):
        if loprec is None:
            loprec = self.loprec
        r = self.raw
        if not hiprec is None:
            r -= mask_prec(self.raw, hiprec)
        return float_ex(r, loprec)

def rand_float_ex(hiprec, loprec):
    return float_ex(random() * prec2val(hiprec), loprec)

def _2list(val):
    if not hasattr(val, '__iter__'):
        return [val]
    else:
        return val

class fractal(object):

    def __init__(self):
        pass

    def make_frame(self, *args):
        raise NotImplementedError()

class fractal_frame(object):

    def __init__(self, fractal):
        self.fractal = fractal

    def get_detail(self, *args):
        raise NotImplementedError()

    def __contains__(self, vals):
        vals = _2list(vals)
        try:
            self.get_detail(*vals)
        except:
            return False
        else:
            return True


from baker import baker_unfolded, baker_unfolded_inv, plot_histories

def concat_nocheck(v1, v2):
    return float_ex(v1.raw + v2.raw, v2.loprec)

def fill_prec_rand(val, loprec, hiprec = None):
    if val.loprec <= loprec:
        return float_ex(val.raw, loprec)
    else:
        if hiprec is None:
            hiprec = val.loprec
        else:
            hiprec = min(hiprec, val.loprec)
        return concat_nocheck(val, rand_float_ex(hiprec, loprec))

def rev_0fltx(val):
    s = val.raw
    r = 0
    for i in xrange(-val.loprec):
        s *= 2
        r += (int(s) & 1) << i
    return r

class baker_frac(fractal):

    def __init__(self, period, rprec):
        super(baker_frac, self).__init__()
        self.period = period
        self.rprec = rprec

    def make_frame(self, x, y):
        if not (0 <= x < 1 and 0 <= y < 1):
            raise ValueError('invalid value')
        x = fill_prec_rand(x, -self.rprec)
        y = fill_prec_rand(y, -self.rprec)
        print x, y
        center_seq = rev_0fltx(y) + x
        rev_center_seq = rev_0fltx(x) + y
        print center_seq, rev_center_seq
        return baker_frac_frame(self, center_seq, rev_center_seq)

    def get_seq_detail(self, seq, val, pos):
        pos = pos % self.period
        if pos >= self.period / 2:
            pos -= self.period
        uprec = self.period - 2 * self.rprec
        dst_lp = default_lowest_prec(val)
        dst = (prec2val(pos) * seq).mask(0, None)
        chk = True
        while dst.loprec > dst_lp:
            if dst.loprec < val.loprec:
                dm = dst.mask(None, val.loprec)
                if chk and not dm == val:
                    raise ValueError('not contains {0} should be {1}'.format(dm, val))
            else:
                vm = val.mask(None, dst.loprec)
                if not vm == dst:
                    raise ValueError('not contains {0} should be {1}'.format(vm, dst))
            nxt_lp = dst.loprec - uprec
            if nxt_lp < val.loprec:
                chk = False
                if dst.loprec > val.loprec:
                    dst = fill_prec_rand(val, nxt_lp, 0)
                else:
                    dst = fill_prec_rand(dst, nxt_lp, 0)
            else:
                dst = val.mask(None, nxt_lp)
            pos -= self.period
            assert pos + self.rprec == dst.loprec or dst.loprec <= dst_lp
            dst = concat_nocheck(dst, prec2val(pos) * seq)
        return dst

class baker_frac_frame(fractal_frame):

    def __init__(self, fractal, center_seq, rev_center_seq):
        super(baker_frac_frame, self).__init__(fractal)
        self.center_seq = center_seq
        self.rev_center_seq = rev_center_seq

    def get_detail(self, x, y, t):
        pass



