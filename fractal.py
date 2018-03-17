
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

from sys import float_info as _float_info

FCAP_MAX_PRECISION = _float_info.mant_dig
FEX_MAX_PRECISION = 30

def highest_prec(val):
    #return np.floor(np.log2(abs(val))) + 1
    m, e = np.frexp(val)
    return e

def prec_info(val):
    m, e = np.frexp(val)
    h = e
    l = e
    v = 0
    while not m.is_integer():
        m *= 2
        l -= 1
        v += 1
    return h, v, l

def mask_prec(val, lp, hp = None):
    if hp is None:
        hp = highest_prec(val)
    #lp = hp - maxp
    #minf = np.exp2(lp)
    minf = 2 ** int(lp)
    #print lp, minf, np.floor(val / minf)
    return np.floor(val / minf) * minf

def is_divided(s, d, r = None):
    if r is None:
        r = s / d
    ms, es = np.frexp(s)
    md, ed = np.frexp(d)
    mr, er = np.frexp(r)
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
    
    def __new__(cls, val, fractal, context,
                dprec = FEX_MAX_PRECISION,
                loprec = None):
        hiprec, _, vlp = prec_info(val)
        minlp = hiprec - FCAP_MAX_PRECISION
        assert vlp >= minlp
        if loprec is None:
            loprec = hiprec - dprec
        if loprec < minlp:
            raise ValueError('float64 overflow.')
        if loprec > vlp:
            loprec = vlp
        ov, eq, rd = _c_val_isin(val, loprec, fractal, context)
        if rd > 0:
            loprec += rd
            val = mask_prec(val, loprec, hiprec)
        if eq:
            return val
        elif ov:
            inst = super(float_ex, cls).__new__(cls, val)
            inst.fractal = fractal
            inst.context = context
            inst.hiprec = hiprec
            inst.loprec = loprec
            return inst
        else:
            raise ValueError('not in the fractal:{0}'.format(val))

    def __init__(self, val, *args):
        super(float_ex, self).__init__(val)

    def __expand__(self, val, mname, *args):
        _chk = lambda mn, lst: reduce(lambda r, v: r or v in mn, lst, False)
        def _prec(val):
            if hasattr(val, 'hiprec'):
                return val.hiprec, val.hiprec - val.loprec, val.loprec
            else:
                return prec_info(val)
        shp, svp, slp = _prec(self)
        if len(args) > 0:
            dst = args[0]
            dhp, dvp, dlp = _prec(args[0])
            maxhp = max(shp, dhp)
            minlp = min(slp, dlp)
        else:
            dst = None
        if _chk(mname, ['add', 'sub']):
            maxrlp = minlp
        elif 'mul' in mname:
            maxrlp = slp + dlp
        elif mname == '__div__':
            if isinstance(dst, float_ex):
                raise TypeError('unsupported operand.')
            if not is_divided(self, dst, val):
                raise ValueError('is not divided.')
            maxrlp = minlp
        else:
            if not dst is None:
                raise TypeError('unsupported operand.')
            maxrlp = slp
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



