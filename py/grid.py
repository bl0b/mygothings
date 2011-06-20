# -*- coding: utf-8 -*-
__all__ = ( 'grid_item', 'intersection', 'group', 'coord', 'position', 'grid_system', 'connex', 'group_union', 'area' )

from utils import *
import re
from properties import *
from direction import *

# Define the goban as a graph

def connex(S):
    return set(( x.group.intersection(S) for x in S ))


def group_union(grid, args):
    return reduce(lambda a, b: a.update(b) or a, args, group(grid))
 
neighbour_score = lambda i, c: reduce(lambda a, b: a+iscore(c, b), i.neighbours, 0) 
area = lambda i: \
    reduce(lambda a, b: a.update(b) or a,
           i.group.nth_neighbours_iter(
               lambda x: x.color is None,
               lambda x: x.color is None and neighbour_score(x, i.color)>=0),
           group(i.grid))

def fuzzy_group(a):
    if type(a) is intersection:
        a = a.group
    ga = group(a.grid)
    ga.update(a)
    if a.color is None:
        return ga
    count = -1
    cur = a
    #print ">>>>>>>>>", a
    while count!=len(ga):
        #print len(ga), count
        count=len(ga)
        al = cur.liberties
        #print "new liberties", al
        n2n3 = al.neighbours.union(al.liberties.neighbours)
        #print "neighbours[2,3]", n2n3
        n = reduce(lambda a, b: a.update(b) or a,
                   (x.group for x in n2n3 if x not in a and x.color is a.color), group(a.grid))
        #print "discovered", n
        ga.update(n)
        cur = n
    #print ">>>>>>>>>", a, ga
    return ga


class grid_item(property_container):
    def __init__(self, grid):
        property_container.__init__(self)
        self.grid = grid

class intersection(grid_item):
    #__metaclass__ = properties
    rep = {
        None:u'⋅',
        BLACK:u'@',
        WHITE:u'@',
        HOSHI:u'+',
        KO:term.RED+u'⋅'
    }
    def __init__(self, grid, c, heightx, heighty, is_hoshi) :
        grid_item.__init__(self, grid)
        self.c = c
        self.W = None
        self.E = None
        self.S = None
        self.N = None
        self.n2o_ = {}
        self.o2n_ = {}
        self.heightx = heightx
        self.heighty = heighty
        self.neighbours = group(grid)
        #self.color = None
        self._group = None
        #self.active_ko = False
        self.is_hoshi = is_hoshi
        self.height = (self.heightx, self.heighty)
        self.min_height = min(self.heightx, self.heighty)
    liberties = cached_property(lambda self: group(self.grid, [ i for i in self.neighbours if i.color is None ]))
    __colifnko = staticmethod(lambda c: c!=KO and c or None)
    color = property(
        lambda self: intersection.__colifnko(self.grid.current.xy2c(self.c.x, self.c.y)),
        lambda self, v: self.grid.current.setc(self.c.x, self.c.y, v)
    )
    def compute_neighbour_vs_orientation(self):
        for i, o in ((self.W, WEST), (self.S, SOUTH), (self.N, NORTH), (self.E, EAST)):
            if i:
                self.n2o_[i] = o
                self.o2n_[o] = (i,)
            else:
                self.o2n_[o] = tuple()
        for i, o in (((self.W, self.N), NORTHWEST), ((self.S, self.W), SOUTHWEST), ((self.N, self.E), NORTHEAST), ((self.E, self.S), SOUTHEAST)):
            if i:
                self.n2o_[i] = o
                self.o2n_[o] = i
            else:
                self.o2n_[o] = tuple()
    def n2o(self, x):
        return x in self.n2o_ and self.n2o_[x] or UNDEF
    def o2n(self, x):
        return x in self.o2n_ and self.o2n_[x] or tuple()
    def __set_active_ko(self, v):
        self.grid.current.setc(self.c.x, self.c.y, v and KO or None)
        if v: 
            if self.grid.current.active_ko:
                self.grid.current.active_ko.color = None
            self.grid.current.active_ko = self
    active_ko = cached_property(
        lambda self: self.grid.current.xy2c(self.c.x, self.c.y)==KO,
        __set_active_ko
    )
    def __str__(self):
        return str(self.c)
    def __repr__(self):
        return str(self.c)
    def colorize(self, color, hilite):
        if color is None:
            return self.active_ko and term.RED or hilite and term.BOARD_HILITE or term.BOARD
        elif color==WHITE:
            return hilite and term.WHITE_HILITE or term.WHITE
        elif color==BLACK:
            return hilite and term.BLACK_HILITE or term.BLACK
    def prettyprint(self, hilite, vec=None):
        return self.colorize(self.color, hilite)+(
            self.color and intersection.rep[self.color]
            or
            type(vec) is direction and self.colorize(vec.color, hilite)+vec.value
            or
            intersection.rep[self.is_hoshi and HOSHI or None])
    def __group(self):
        if not self._group:
            def greedy_group(x):
                for n in x.neighbours:
                    if n.color==self.color and n._group is not self._group:
                        n._group=self._group
                        self._group.add(n)
                        greedy_group(n)
            self._group = group(self.grid, [self])
            self._group.add(self)
            greedy_group(self)
        return self._group
    def compute_grp(self):
        grp = group(self.grid)
        grp.add(self)
        def greedy_group(x):
            for n in (k for k in x.neighbours if k.color is self.color and k not in grp):
                n.group = grp
                grp.add(n)
                greedy_group(n)
        greedy_group(self)
        return grp
    group = cached_property(compute_grp, lambda s, x: x)



coord_re = re.compile("^[a-jk-zA-JK-Z]+[1-9][0-9]*$")


class coord(object):
    alphabet = [ chr(x) for x in xrange(ord('a'), ord('j')) ] \
             + [ chr(x) for x in xrange(ord('k'), ord('z')+1) ] # length = 25
    @staticmethod
    def match(x):
        return coord_re.match(x)
    @staticmethod
    def X(x):
        ret = coord.alphabet[x%25]
        while True:
            x /= 25
            if x==0:
                break
            ret = coord.alphabet[(x-1)%25] + ret

        return ret

    @staticmethod
    def Y(y):
        return str(1+y)

    def __init__(self, grid, *a):
        #print 'new coord', a
        if type(a[0]) is str:
            self.s = a[0]
            self.x, self.y = coord.from_xy(grid, self.s)
        else:
            if type(a[0]) is tuple:
                self.x, self.y = a[0]
            else:
                self.x = a[0]
                self.y = a[1]
            self.s = coord.X(self.x) + coord.Y(self.y)
        self.xy = (self.x, self.y)

    def __str__(self):
        return self.s

    #xyinv = lambda self, size: (self.x, size-1-self.y)

    @staticmethod
    def from_xy(grid, s):
        x=0
        y=0
        for c in s.lower():
            if c in coord.alphabet:
                x*=25
                x+=1+coord.alphabet.index(c)
            else:
                y*=10
                y+=int(c)
        return x-1, grid.size-y


class grid_item_set(grid_item, set):
    def __init__(self, grid, _set=None):
        if _set is not None:
            set.__init__(self, _set)
        else:
            set.__init__(self)
        grid_item.__init__(self, grid)

    intersection = lambda self, b: type(self)(self.grid, set.intersection(self, b))
    difference = lambda self, b: type(self)(self.grid, set.difference(self, b))
    union = lambda self, b: type(self)(self.grid, set.union(self, b))
    __sub__ = lambda self, b: type(self)(self.grid, set.__isub__(self, b))
    __add__ = lambda self, b: type(self)(self.grid, set.union(self, b))




class group(grid_item_set):
    #__metaclass__ = properties
    def __init__(self, grid, _set=None):
        grid_item_set.__init__(self, grid, _set)
    def merge(self, g):
        for i in g:
            i.group = self
            self.add(i)

    color = cached_property(lambda self: min(self).color)
    #neighbours = cached_property(lambda self: group(a.grid, reduce(lambda a, b: a.update(b.neighbours) or a, self, set())-self))
    neighbours = property(lambda self: group(self.grid, reduce(lambda a, b: a.update(b.neighbours) or a, self, set())-self))
    liberties = cached_property(lambda self: reduce(lambda a, b: b.color is None and a.add(b) or a, self.neighbours, group(self.grid)))
    surrounding_groups = cached_property(lambda self: set(filter(lambda x: x and x is not self, [x.group for x in self.neighbours if x.color is not None]))-self)
    group = property(lambda self: self)
    fuzzy_group = cached_property(fuzzy_group)
    eyes = cached_property(lambda self:
                           filter(lambda x: reduce(lambda a, b:
                                                   a and (b.color is self.color),
                                                   x.group.surrounding_groups, True),
                                  reduce(lambda a, b: a.add(b.group) or a,
                                         self.group.fuzzy_group.liberties, set())))

    def nth_neighbours(self, n, flt=lambda i: True):
        if n==0:
            return self
        elif n==1:
            return self.neighbours
        n0 = set()
        n1 = self
        n2 = group(self.grid)
        n2_exc = group(self.grid)
        for x in n1.neighbours:
            if flt(x):
                n2.add(x)
            else:
                n2_exc.add(x)
        while n > 1:
            n -= 1
            n0 = n1
            n2_exc.update(filter(lambda i: not flt(i), n2))
            n2.difference_update(n2_exc)
            n1 = n2
            n2 = group(self.grid, n1.neighbours-n1-n0-n2_exc)
            n2_exc.update(n2_exc.neighbours)
        return n2

    def nth_neighbours_iter(self, flt=lambda i: True, propag_flt=lambda i: True):
        n0 = set()
        n1 = self
        n2 = group(self.grid)
        n2_exc = group(self.grid)
        for x in n1.neighbours:
            if flt(x):
                n2.add(x)
            else:
                n2_exc.add(x)
        while len(n2)>0:
            #n -= 1
            n0 = n1
            bad = group(self.grid, filter(lambda i: not flt(i), n2))
            yield n2-bad
            n2_exc.update(bad)
            n2_exc.update(bad.neighbours)
            n2_exc.update(n2_exc.neighbours)
            n2.difference_update(n2_exc)
            n1 = n2
            n2 = group(self.grid, n1.neighbours-n1-n0-n2_exc)
        #return n2

#    @staticmethod
#    def __good_bad(N, flt):
#        good = group(N.grid)
#        bad = group(N.grid)
#        for n in N:
#            if flt(n):
#                good.add(n)
#            else:
#                bad.add(n)
#        return good, bad
#    def nth_neighbours_iter(self, match_flt=lambda i: True, propagate_flt=lambda i: True):
#        n0 = None
#        n1 = self
#        n2, n2_exc = group.__good_bad(self.neighbours, match_flt)
#        while len(n2)>0:
#            print
#            print n2
#            print n2_exc
#            yield n2
#            propag = group(self.grid, (x for x in n2 if propagate_flt(x)))
#            good = group(self.grid)
#            bad = group(self.grid)
#            for x in (x for x in propag.neighbours if x not in n2 and x not in n2_exc):
#                if match_flt(x):
#                    good.add(x)
#                else:
#                    bad.add(x)
#            #n2, bad = group.__good_bad(good, match_flt)
#            n2 = good
#            n2_exc.update(bad)
#            n2_exc.update(bad.neighbours)
#            #n2_exc.update(bad.neighbours)
#
#            #n2 = good.difference(n2-n2_exc)
#            #n2 = group(self.grid)
#            #for n in N.neighbours:
#            #    if n in n2_exc:
#            #        continue
#            #    elif flt(n):
#            #        n2.add(n)
#            #    else:
#            #        n2_exc.add(n)
#            #n2_exc.update(n2_exc.neighbours)
#
#            #n2 = group(self.grid, (n for n in n2.neighbours if n not in n2_exc and flt(n)))

    def __hash__(self):
        return reduce(lambda a, b: a+hash(b), self, 0)

    def filter(self, p):
        map(self.remove, filter(lambda x: not p(x), self))
        return self


class position(list):
    col2bits = { WHITE:1, BLACK:2, None:0, KO:3 }
    bits2col = [ None, WHITE, BLACK, KO ]
    __xy2i = lambda self, x, y: 2*(y*self.size+x)
    __xyc2l = lambda self, x, y, col: position.col2bits[col] << self.__xy2i(x, y)
    __xymask = lambda self, x, y: 3 << self.__xy2i(x, y)
    xy2c = lambda self, x, y: position.bits2col[(self.data >> self.__xy2i(x, y)) & 3]
    def setc(self, x, y, c):
        self.data &= ~self.__xymask(x, y)
        self.data |= self.__xyc2l(x, y, c)
        return self
    def __init__(self, size, parent=None):
        self.size = size
        self.active_ko = None
        if self.size==0:
            self.data = 0
            return
        if parent is None:
            self.data = long()
            self.parent = position(0)
        else:
            self.data = long(parent.data)
            self.parent = parent
        self.parent.append(self)
    def pack(self, grid):
        self.data = long()
        for row in grid:
            for i in row:
                self.data <<= 2
                self.data |= position.col2bits[i]
    def unpack(self):
        return [
            [ self.xy2c(x, y) for x in xrange(self.size) ]
            for y in xrange(self.size)
        ]
    def __str__(self):
        return str(self.data)+":"+list.__str__(self)
    def __repr__(self):
        return repr(self.data)+":"+list.__repr__(self)




class grid_system(grid_item):
    #__metaclass__ = properties
    def __init__(self, size=None):
        if size is not None:
            self.init(size)
        grid_item.__init__(self, self)
    def init(self, size):
        self.intersections = {}
        ctr = (size)/2
        self.size = size
        hoshi = ( size>=13 and 4 or 3, (size+1)/2 )
        for (x, y) in iterate_coords(size):
            hx = x>ctr and size-x or 1+x
            hy = y>ctr and size-y or 1+y
            i = intersection(self, coord(self, x, self.size-1-y), hx, hy, hx in hoshi and hy in hoshi)
            self.intersections[x, y] = i
        for (x, y) in iterate_coords(size):
            i = self.intersections[coord(self, x,y).xy]
            if x>0:
                i.W = self.intersections[coord(self, x-1, y).xy]
                i.neighbours.add(i.W)
            if x<(size-1):
                i.E = self.intersections[coord(self, x+1, y).xy]
                i.neighbours.add(i.E)
            if y>0:
                i.N = self.intersections[coord(self, x, y-1).xy]
                i.neighbours.add(i.N)
            if y<(size-1):
                i.S = self.intersections[coord(self, x, y+1).xy]
                i.neighbours.add(i.S)
            i.compute_neighbour_vs_orientation()
        self.tree = position(self.size, position(0))
        self.current = self.tree
    def __getitem__(self, *xy):
        return self.intersections[coord(self, *xy).xy]
    def __setitem__(self, *xy):
        value = xy.pop()
        self.intersections[coord(self, *xy).xy] = value
    def fork(self):
        dat = self.current.data
        self.current = position(self.size, self.current.parent)
        self.current.data = long(dat)
        return self.current
    def delete_position(self, pos):
        pos.parent.remove(pos)
        if self.current == pos:
            self.current = self.current.parent[self.current.parent.index(self.current)-1]
        #del pos
    def previous_variation(self):
        c = self.current
        p = c.parent
        self.current = p[ (p.index(c)+len(p)-1) % len(p) ]
    def next_variation(self):
        c = self.current
        p = c.parent
        self.current = p[ (p.index(c)+len(p)+1) % len(p) ]
    def go_back(self, n=1):
        for k in xrange(n):
            if self.current.parent.data != 0:
                self.current = self.current.parent
    def go_forward(self, n=1):
        for k in xrange(n):
            if self.current[0]:
                self.current = self.current[0]
    def commit_position(self):
        c = self.current
        self.current = position(self.size, c)
    groups = cached_property(lambda self: list(set([ x.group for x in self.intersections.values() if x.color ])))
    territories = cached_property(lambda self: list(set([ x.group for x in self.intersections.values() if not x.color ])))
    def merge_groups(self, g1, g2):
        g1.merge(g2)
        return g1
    def vspace(self):
        return dict(((i, direction()) for i in self.intersections.values()))

#    def remove_from_group(self, g, s):
#        g.remove(s)
#        if len(g)==0:
#            try:
#                self.groups.remove(g)
#            except ValueError, ve:
#                pass

