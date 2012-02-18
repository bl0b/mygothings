
from direction import *
from grid import *
from utils import *

# around one stone
# 1-stone shapes :
#   a (0)
# 2-stone shapes :
#   ab (1)
# 3-stone shapes :
#   bac (I)    ab (L)
#              c
# 4-stone shapes :
#   bac (T)
#    d
# 5-stone shapes :
#    b
#   cad (X)
#    e

# 0 < 1 < {{I,L}}; I |< L ; L |< I; {{L, I}} < T < X;

# A     B       A IN B
# 0     *       true
# 1     *       true
# I     {T,X}   true
# L     {T,X}   true
# T     {X}     true

shape_constant = lambda k,n=0: ((k<<1)+n)
shape_id = lambda s: s>>1

shape_0 = shape_constant(0)
shape_1 = shape_constant(1)
shape_I = shape_constant(2,0)
shape_L = shape_constant(2,1)
shape_T = shape_constant(3,0)
shape_X = shape_constant(4,0)

def a_in_b(a, b):
    s0 = int(b[shape_0])
    s1 = int(b[shape_1])
    sI = int(b[shape_I])
    sL = int(b[shape_L])
    sT = int(b[shape_T])
    sX = int(b[shape_X])

    sX -= a[shape_X]
    if sX < 0:
        return False
    sT -= a[shape_T]-sX
    if sT < 0:
        return False
    sL -= a[shape_L]-sT
    if sL < 0:
        return False
    sI -= a[shape_I]-sT
    if sI < 0:
        return False
    s1 -= a[shape_1]-sL-sI+sT
    if s1 < 0:
        return False
    s0 -= a[shape_0]-s1
    if s0 < 0:
        return False
    return True


def a_is_b(a, b): # very useful!
    return a==b



#def a_in_b(a, b):
#    ia = iter(a)
#    ib = iter(b)
#    try:
#        ret = True
#        while ret:
#            va = ia.next()
#            print "va", va
#            try:
#                vb = va-1
#                while shape_id(vb)<shape_id(va) or shape_id(vb)==shape_id(va) and va!=vb:
#                    vb = ib.next()
#                    print "vb", vb
#            except StopIteration, si:
#                return False
#            ret = shape_id(va) < shape_id(vb) or va == vb
#            print va, shape_id(va), vb, shape_id(vb), ret
#        return ret
#    except StopIteration, si:
#        return True



shape_encoder = {
    0: shape_0,
    1: shape_1,
    (WEST,EAST): shape_I,
    (WEST,NORTH): shape_L,
    (WEST,SOUTH): shape_L,
    (EAST,WEST): shape_I,
    (EAST,NORTH): shape_L,
    (EAST,SOUTH): shape_L,
    (NORTH,SOUTH): shape_I,
    (NORTH,WEST): shape_L,
    (NORTH,EAST): shape_L,
    (SOUTH,NORTH): shape_I,
    (SOUTH,WEST): shape_L,
    (SOUTH,EAST): shape_L,
    3: shape_T,
    4: shape_X,
}

color_encoder = {
}



def encode_shape(g, grp):
    ret = { shape_0:0, shape_1:0, shape_I:0, shape_L:0, shape_T:0, shape_X:0 }
    for s in (shape_encoder[len(t)==2 and t or len(t)]
                for t in (tuple((s.n2o(x) for x in s.neighbours if x in grp))
                          for s in grp)):
        ret[s]+=1
    return ret





minus = lambda x : -x
plus = lambda x: x


def xy(fx, fy):
    return lambda x, y, c='?', h=False, m=0: (fx(x), fy(y), c, h, m)

def yx(fx, fy):
    return lambda x, y, c='?', h=False, m=0: (fy(y), fx(x), c, h, m)

SC_SELF='s'
SC_EMPTY='.'
SC_FOE='f'
SC_ANY='?'
SC_UNUSED=' '
SC_NOTSELF='S'
SC_NOTFOE='F'
SC_NOTEMPTY='*'
SC_HOTSPOT='!'


transpose = (
    xy(plus, plus), xy(plus, minus), xy(minus, plus), xy(minus, minus),
    yx(plus, plus), yx(plus, minus), yx(minus, plus), yx(minus, minus),
)

def normalize_coords(s):
    s = sorted(s)
    x0, y0, c, h, mgl = s[0]
    return tuple(((x-x0, y-y0, c, h, mgl) for x, y, c, h, mgl in s))

def shape_rel_coords(s, colconv = lambda c: SC_ANY, hotspots=set()):
    s0 = min(s)
    if type(s0) is intersection:
        x0 = s0.c.x
        y0 = s0.c.y
        return normalize_coords(((i.c.x-x0, i.c.y-y0, colconv(i.color), i in hotspots, 0) for i in s))
    elif type(s0) is tuple:
        x0 = s0[0]
        y0 = s0[1]
        return normalize_coords(((x-x0, y-y0, c, h, mgl) for x, y, c, h, mgl in s))

def shape_from_strings(strlist):
    def gen_shape():
        hotspot = False
        min_group_libs = 0
        for y, s in xzip(xrange(len(strlist)), strlist):
            for x, c in xzip(xrange(len(s)), s):
                if c>='0' and c<='9':
                    min_group_libs *= 10
                    min_group_libs += ord(c)-ord('0')
                if c is SC_HOTSPOT:
                    hotspot = True
                    continue
                if c is not SC_UNUSED:
                    yield (x, y, c, hotspot, min_group_libs)
                    hotspot = False
                    min_group_libs = 0
    return normalize_coords(gen_shape())

def all_rel_shapes(s):
    src = shape_rel_coords(s)
    ret = set()
    return set((normalize_coords((T(x, y, c, h, m) for x, y, c, h, m in src)) for T in transpose))

class shape_tree(dict):
    match_calls = 0
    def __init__(self):
        dict.__init__(self)
        self.payload = None
    def from_shape(self, s, payload):
        if len(s)==0:
            self.payload = payload
        else:
            x = s[0]
            if not x in self:
                self[x] = shape_tree()
            #print s
            #if len(s)>0:
            self[x].from_shape(s[1:], payload)
            #else:
            #    self.payload = payload
        return self

    # cc is short for color conversion.
    # each __ccXY says which SC_* matches to BLACK or WHITE.
    __ccBW = set([(SC_ANY, BLACK), (SC_ANY, WHITE), (SC_ANY, None), (SC_SELF, BLACK), (SC_FOE, WHITE), (SC_EMPTY, None)])
    __ccWB = set([(SC_ANY, BLACK), (SC_ANY, WHITE), (SC_ANY, None), (SC_SELF, WHITE), (SC_FOE, BLACK), (SC_EMPTY, None)])

    def __match(self, g, gcol, x0, y0, cc, grp, hsgrp, results):
        shape_tree.match_calls += 1
        if self.payload:
            results.add((group(g, grp), group(g, hsgrp), self.payload))
        for (x,y,c,h,mgl), st in self.iteritems():
            try:
                coord = (x+x0, y+y0)
                i, gc = gcol[coord]
                if (c, gc) in cc and (mgl==0 or len(i.group.liberties)>=mgl):
                    tmp=(i,)
                    st.__match(g, gcol, x0, y0, cc, grp+tmp, h and hsgrp+tmp or hsgrp, results)
                #print i, x, y, c, st, h
            except KeyError, ke:
                continue

    def match(self, g, gcol, x0, y0, ret={BLACK:set(), WHITE:set()}):
        self.__match(g, gcol, x0, y0, shape_tree.__ccBW, tuple(), tuple(), ret[BLACK])
        self.__match(g, gcol, x0, y0, shape_tree.__ccWB, tuple(), tuple(), ret[WHITE])
        return ret

    def match_all(self, g, zone=None):
        shape_tree.match_calls = 0
        c = chrono()
        ret = { BLACK:set(), WHITE:set() }
        # using gcol is MUCH faster than accessing i.color !
        if zone is None:
            gcol = dict(( (k, (i, i.color)) for k, i in g.intersections.iteritems() ))
        else:
            gcol = dict(( (i.c.xy, (i, i.color)) for i in zone ))
        for x, y in iterate_coords(g.size):
            #ret.update(self.match(g, x, y))
            self.match(g, gcol, x, y, ret)
        print "took", float(c), "to search whole grid, with", shape_tree.match_calls, "total recursive calls."
        return ret

    def from_strings(self, strings, payload):
        sfs = shape_from_strings(strings)
        ars = all_rel_shapes(sfs)
        for a in ars:
            self.from_shape(a, payload)


aji_shapes = (
    (('sf', 'f!'), 'cut'),
)

nakade_shapes = {
    'center': (
        # those apply to empty regions
        (('fsf', 's!s', ' s '), ('false_eye', 'alive_if_other_eyes')),
        (('sfs', 'f!f', 'f.f'), ('throw-in', 'reduce_eyespace')),
        (('ssss ', 's.!.s', 'ssss '), ('three', 'unsettled')),
        (('ssss ', 's.!.s', ' ssss'), ('three', 'unsettled')),
        ((' ssss ', 's.!!.s', ' ssss '), ('four_in_a_row', 'alive')),
    ),
    'side': (
        (('',), 'todo')
    )
}
