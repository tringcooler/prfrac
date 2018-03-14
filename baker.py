
import numpy as np
import matplotlib.pyplot as plt

def baker_unfolded(ar):
    x, y = ar
    x2 = 2. * x
    x2f = np.floor(x2)
    return np.array([x2 - x2f, (y + x2f) / 2.])

def baker_unfolded_inv(ar):
    x, y = ar
    y2 = 2. * y
    y2f = np.floor(y2)
    return np.array([(x + y2f) / 2., y2 - y2f])

def baker_map(src, n = 1, inv = False):
    if inv:
        f = baker_unfolded_inv
    else:
        f = baker_unfolded
    dst = src
    for i in xrange(n):
        dst = np.apply_along_axis(f, 1, dst)
    return dst

class _range2slice(object):
    def __getitem__(self, rngs):
        return rngs
r2s = _range2slice()

def rand_delt(s, pr = 0.001):
    sign = np.random.randint(2)
    delt = np.random.random() * pr / 2
    r = s + (sign * 2 - 1) * delt
    return min(max(r, 0), 1)
v_rand_delt = np.vectorize(rand_delt)

class _range_src(object):

    def __getitem__(self, rngs):
        mg = np.mgrid.__getitem__(rngs)
        dn = len(rngs)
        for i in xrange(dn, 0, -1):
            mg = mg.swapaxes(0, i)
        return mg.reshape(-1, dn)
range_src = _range_src()

class range_filter(object):

    def __init__(self, src):
        self.src = src

    def __getitem__(self, rngs):
        cond = None
        def _andc(c):
            if cond is None:
                return c
            else:
                return np.logical_and(cond, c)
        if not hasattr(rngs, '__iter__'):
            rngs = [rngs]
        for i, rng in enumerate(rngs):
            srct = self.src[:,i]
            if type(rng) == slice:
                if not rng.start is None:
                    cond = _andc(srct >= rng.start)
                if not rng.stop is None:
                    cond = _andc(srct < rng.stop)
            else:
                cond = _andc(srct == rng)
        return cond

def _init_test(src_slc):
    pr = src_slc[0].step
    s = range_src[src_slc]
    s = v_rand_delt(s, pr)
    return s, pr

def test(src_slc, dst_slc, n = 10):
    s, pr = _init_test(src_slc)
    r = baker_map(s, n)
    f = range_filter(r)[dst_slc]
    ds = s[f]
    dr = r[f]
    print len(s), len(dr)
    return s, r, ds, dr

def test2(src_slc, dst_slc, n = 10):
    s, pr = _init_test(src_slc)
    info = []
    r = s
    for i in xrange(n):
        r = baker_map(r)
        f = range_filter(r)[dst_slc]
        info.append([
            r, f,
        ])
    return s, info

def _fit_shape(n, sc):
    x = np.sqrt(n * sc)
    y = np.sqrt(n / sc)
    ymin = max(np.floor(y), 1.)
    xmax = np.ceil((ymin + 1) * sc)
    yr = ymin
    while True:
        xr = np.ceil(n / yr)
        if xr <= xmax:
            break
        yr += 1
    return int(xr), int(yr)

def plots(n):
    sc = 4./3.
    nx, ny = _fit_shape(n, sc)
    #f, sbplts = plt.subplots(ny, nx, sharex='col', sharey='row')
    f, sbplts = plt.subplots(ny, nx, sharex=True, sharey=True)
    return np.array(sbplts).reshape(-1)[:n]

def plot_history(src, sbplts, color = 'b'):
    n = len(sbplts)
    def _plt(s, i):
        sbplts[i].plot(s[:,0], s[:,1], color + '.')
    dst = src
    _plt(dst, 0)
    for i in xrange(1, n):
        dst = baker_map(dst)
        _plt(dst, i)

def plot_histories(src, dsts, sbplts):
    n = len(sbplts) - 1
    colors = ['b', 'r', 'g', 'y']
    pn = min(max(len(colors), 0), n)
    color = lambda i: colors[n - i]
    def _plt(s, i, c):
        sbplts[i].plot(s[:,0], s[:,1], c + '.')
    for i in xrange(n - pn, n):
        flt = dsts[i][1]
        c = color(i + 1)
        _plt(src[flt], 0, c)
        for j in xrange(0, n):
            dst = dsts[j][0]
            _plt(dst[flt], j + 1, c)

if __name__ == '__main__':
    pr = .0001
    nm = 20
    src_slc = r2s[.78:.83:pr, .14:.19:pr]
    dst_slc = r2s[.68:.73, .24:.29]
    #s, r, ds, dr = test(src_slc, dst_slc, nm)
    #idr1 = baker_map(dr, 1, inv = True)
    #plt.plot(ds[:,0], ds[:,1], 'r.')
    #plt.plot(dr[:,0], dr[:,1], 'b.')
    #plt.plot(idr1[:,0], idr1[:,1], 'g.')
    #plt.axis('equal')
    #plt.show()
    s, rs = test2(src_slc, dst_slc, nm)
    sbplts = plots(nm + 1)
    plot_histories(s, rs, sbplts)
    plt.show()

