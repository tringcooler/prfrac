
import numpy as np
from baker import baker_map, plot_histories

class meta_arith_ex(type):

    method_names = 'add sub mul neg'.split() 
    
    def __new__(metaname, classname, baseclasses, attrs):
        for mn in meta_arith_ex.method_names:
            mn = '__{:s}__'.format(mn)
            def mdst(mn):
                def _wrapper(self, *args, **kargs):
                    scls = type(self)
                    r = getattr(super(scls, self), mn)(*args, **kargs)
                    return scls(r)
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

    
