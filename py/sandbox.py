# -*- coding: utf-8 -*-
import sys

from sgflib import SGFParser, GameTreeEndError

from colorterm import *

# Define the goban as a graph

WHITE='w'
BLACK='b'
HOSHI='h'
KO='k'



class term(object):
    WHITE=u'\x1B[1;37;46m'
    WHITE_HILITE=u'\x1B[1;37;42m'
    BLACK=u'\x1B[1;30;46m'
    BLACK_HILITE=u'\x1B[1;30;42m'
    BOARD=u'\x1B[1;36;46m'
    BOARD_HILITE=u'\x1B[1;36;42m'
    NORMAL=u'\x1B[0m'
    CLEAR=u'\x1B[2J'
    RED=u'\x1B[1;36;44m'


class cached(object):
    def __init__(self, P):
        self.P = P
        self.position = None
        self.value = None
    def __call__(self, target):
        if target.grid is None:
            return self.P(target)
        if target.grid.current.data != self.position:
            self.position = target.grid.current.data
            self.value = self.P(target)
        return self.value



class grid_item(object):
    def __init__(self, grid):
        self.grid = grid


class intersection(grid_item):
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
        self.heightx = heightx
        self.heighty = heighty
        self.neighbours = group()
        #self.color = None
        self._group = None
        #self.active_ko = False
        self.is_hoshi = is_hoshi
    height = property(lambda self: (self.heightx, self.heighty))
    min_height = property(lambda self: self.heightx<self.heighty and self.heightx or self.heighty)
    liberties = property(lambda self: group([ i for i in self.neighbours if i.color is None ]))
    __colifnko = staticmethod(lambda c: c!=KO and c or None)
    color = property(
        lambda self: intersection.__colifnko(self.grid.current.xy2c(self.c.x, self.c.y)),
        lambda self, v: self.grid.current.setc(self.c.x, self.c.y, v)
    )
    def __set_active_ko(self, v):
        self.grid.current.setc(self.c.x, self.c.y, v and KO or None)
        if v: 
            if self.grid.current.active_ko:
                self.grid.current.active_ko.color = None
            self.grid.current.active_ko = self
    active_ko = property(
        lambda self: self.grid.current.xy2c(self.c.x, self.c.y)==KO,
        __set_active_ko
    )
    def __str__(self):
        return str(self.c)
    def __repr__(self):
        return str(self.c)
    def colorize(self, hilite):
        if self.color is None:
            return self.active_ko and term.RED or hilite and term.BOARD_HILITE or term.BOARD
        elif self.color==WHITE:
            return hilite and term.WHITE_HILITE or term.WHITE
        elif self.color==BLACK:
            return hilite and term.BLACK_HILITE or term.BLACK
    def prettyprint(self, hilite):
        return self.colorize(hilite)+intersection.rep[self.color is None and self.is_hoshi and HOSHI or self.color]
    def __group(self):
        if not self._group:
            def greedy_group(x):
                for n in x.neighbours:
                    if n.color==self.color and n._group is not self._group:
                        n._group=self._group
                        self._group.add(n)
                        greedy_group(n)
            self._group = group([self])
            self._group.add(self)
            greedy_group(self)
            #self._group = group()
            #self._group.add(self)
        return self._group
    group = property(__group)




class coord(object):
    alphabet = [ chr(x) for x in xrange(ord('a'), ord('j')) ] \
             + [ chr(x) for x in xrange(ord('k'), ord('z')+1) ] # length = 25
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

    def __init__(self, *a):
        if type(a[0]) is str:
            self.s = a[0]
            self.x, self.y = coord.from_xy(self.s)
        else:
            self.x = a[0]
            self.y = a[1]
            self.s = coord.X(self.x) + coord.Y(self.y)

    def __str__(self):
        return self.s

    xy = property(lambda self: (self.x, self.y))

    @staticmethod
    def from_xy(s):
        x=0
        y=0
        for c in s.lower():
            if c in coord.alphabet:
                x*=25
                x+=1+coord.alphabet.index(c)
            else:
                y*=10
                y+=int(c)
        return x-1, y-1



class group(set, grid_item):
    def __init__(self, _set=None):
        if _set is not None:
            set.__init__(self, _set)
        else:
            set.__init__(self)
        self.grid = len(self) and min(self).grid or None
    def merge(self, g):
        for i in g:
            i._group = self
            self.add(i)
    def add(self, x):
        set.add(self, x)
        if self.grid is None:
            self.grid = len(self) and min(self).grid or None
    def update(self, iterable):
        set.update(self, iterable)
        if self.grid is None:
            self.grid = len(self) and min(self).grid or None
    color = property(lambda self: min(self).color)
    neighbours = property(lambda self: reduce(lambda a, b: a.update(b.neighbours-self) or a, self, group()))
    liberties = property(lambda self: reduce(lambda a, b: b.color is None and a.add(b) or a, self.neighbours, group()))
    surrounding_groups = property(lambda self: set(filter(lambda x: x and x is not self, [x.group for x in self.neighbours if x.color is not None]))-self)
    group = property(lambda self: self)

    def nth_neighbours(self, n):
        if n==0:
            return self
        elif n==1:
            return self.neighbours
        n0 = set()
        n1 = self
        n2 = self.neighbours
        while n > 1:
            n -= 1
            n0 = n1
            n1 = n2
            n2 = n1.neighbours-n1-n0
        return n2

    def __hash__(self):
        return reduce(lambda a, b: a+hash(b), self, 0)

    def filter(self, p):
        map(self.remove, filter(lambda x: not p(x), self))
        return self






class IllegalMove(Exception) :
    pass

def iterate_box(x1, y1, x2, y2):
    return ( (x, y) for x in xrange(x1, x2+1) for y in xrange(y1, y2+1) )

def iterate_coords(size):
    return ( (x, y) for x in xrange(size) for y in xrange(size) )



def feed(self, gametree, aftermove=lambda g : None) :
    def gen_curs(cursor) :
        def _gen() :
            try :
                while not cursor.atEnd :
                    yield cursor.node
                    cursor.next()
            except GameTreeEndError :
                pass
        return _gen
    def getcolor(node):
        return node.has_key('W') and 'W' or node.has_key('B') and 'B' or None
    colors = { 'W':WHITE, 'B':BLACK }
    cursor = gen_curs(gametree.mainline().cursor())
    for node in cursor() :
        if node.has_key('SZ'):
            #print str(node['SZ'])
            szstr = str(node['SZ'])
            size = int(szstr[szstr.find('[')+1:-1])
            self.init(size)
        else:
            col = getcolor(node)
            if col is not None:
                xy = str(node[col])[2:4]
                x, y = map(lambda x : ord(x)-ord('a'), list(xy))
                print coord(x, y),
                if x==y and x>=self.size:
                    self.add_pass()
                else:
                    #print "new stone", colors[col], coord(x, y)
                    self.add_stone(self.intersections[x, y], colors[col])
                self.commit_position()
                aftermove(self)


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




class grid_system(object):
    def __init__(self, size=None):
        if size is not None:
            self.init(size)
        self.grid = self
    def init(self, size):
        self.intersections = {}
        ctr = (size)/2
        self.size = size
        hoshi = ( size>=13 and 4 or 3, (size+1)/2 )
        for (x, y) in iterate_coords(size):
            hx = x>ctr and size-x or 1+x
            hy = y>ctr and size-y or 1+y
            i = intersection(self, coord(x, y), hx, hy, hx in hoshi and hy in hoshi)
            self.intersections[x,y] = i
        for (x, y) in iterate_coords(size):
            i = self.intersections[x,y]
            if x>0:
                i.neighbours.add(self.intersections[x-1, y])
            if x<(size-1):
                i.neighbours.add(self.intersections[x+1, y])
            if y>0:
                i.neighbours.add(self.intersections[x, y-1])
            if y<(size-1):
                i.neighbours.add(self.intersections[x, y+1])
        self.tree = position(self.size, position(0))
        self.current = self.tree
    def __getitem__(self, *xy):
        return self.intersections[coord(*xy).xy]
    def fork(self):
        dat = self.current.data
        self.current = position(self.size, self.current.parent)
        self.current.data = dat
        return self.current
    def delete_position(self, pos):
        pos.parent.remove(pos)
        if self.current == pos:
            self.current = self.current.parent[self.current.parent.index(self.current)-1]
        del pos
    def previous_variation(self):
        c = self.current
        p = c.parent
        self.current = p[ (p.index(c)+len(p)-1) % len(p) ]
        return self.current
    def next_variation(self):
        c = self.current
        p = c.parent
        self.current = p[ (p.index(c)+len(p)+1) % len(p) ]
        return self.current
    def go_back(self):
        if self.current.parent.data != 0:
            self.current = self.current.parent
        return self.current
    def go_forward(self):
        if self.current[0]:
            self.current = self.current[0]
        return self.current
    def commit_position(self):
        c = self.current
        self.current = position(self.size, c)
        return self.current
    groups = property(lambda self: list(set([ x.group for x in self.intersections.values() if x.color ])))
    territories = property(lambda self: list(set([ x.group for x in self.intersections.values() if not x.color ])))
    def merge_groups(self, g1, g2):
        g1.merge(g2)
        return g1
#    def remove_from_group(self, g, s):
#        g.remove(s)
#        if len(g)==0:
#            try:
#                self.groups.remove(g)
#            except ValueError, ve:
#                pass



class goban(grid_system):
    def __init__(self, size=None):
        grid_system.__init__(self, size)
    def init(self, size, handicap=0, komi=6.5):
        self.prisoners = { BLACK:0, WHITE:0 }
        self.active_ko = None
        self.komi = komi
        grid_system.init(self, size)
    def copy(self):
        g = grid_system.copy(self, goban)
        g.prisoners = self.prisoners.copy()
        g.active_ko = self.active_ko
        return g
    def legal_moves(self, color):
        def is_legal_move(i):
            # it is not allowed to play on a stone, or to capture a ko directly
            if i.color is not None or i.active_ko:
                return False
            if not i.liberties:
                # Check if that stone would capture something OR connects to at least one group that has more than one liberty
                return reduce(lambda a, b:
                                a
                                or
                                b is not None and (
                                  b.group.color!=color and len(b.group.liberties)==1
                                  or
                                  b.group.color==color and len(b.group.liberties)>1   # we don't want to remove the last liberty of a group
                              ),
                              i.neighbours, False)
            return True
        return filter(is_legal_move, self.intersections)
    def detect_ko(self, play, capture):
        #foes = filter(lambda x: x.color is not None and x.color!=play.color, play.neighbours)
        #single[0].active_ko = True
        #self.active_ko = single[0]
        capture.active_ko = True
        self.active_ko = capture
    def add_stone(self, i, color):
        if type(i) is str:
            i = self[i]
        # Detect neighbouring groups
        A = [] # allies
        E = [] # enemies
        if color:
            # check for legal moves
            if i==self.active_ko:
                raise IllegalMove("ko")
            if self.active_ko:
                self.active_ko.active_ko = False
            self.active_ko = None
            if i.color!=None:
                raise IllegalMove("stone")
        liberties_total = 0
        for n in i.neighbours:
            if n.color is not None:
                if n.color==color:
                    gl = A
                else:
                    gl = E
                gl.append(n.group)
                liberties_total += len(n.group.liberties)-1
            else:
                liberties_total+=1
#        if liberties_total==0:
#            raise IllegalMove("suicide")
        cap_count = 0
        capture = None
        if color and E:
            # check for a direct ko situation
#            if len(E)==1 and len(E[0])==1 and i.liberties is None:
#                self.active_ko = min(E[0])
#                self.active_ko.active_ko = True
            captured = filter(lambda x: len(x.liberties)==1, E)
            #print "captures :", zip(captured, map(lambda x : x.liberties, captured))
            tmp = None
            for g in captured:
                for s in g:
                    s.color=None
                    cap_count+=1
                    capture = s
                #self.groups.remove(g)
                self.prisoners[color] += len(g)
        if color and cap_count==0 and liberties_total==0:
            raise IllegalMove("suicide")
        i.color=color
        i._group=None
        if A:
            g = reduce(lambda a, b: self.merge_groups(a, b), A)
            i._group=g
            g.add(i)
        else:
            i._group=group()
            i._group.add(i)
        if cap_count==1 and len(i.group)==1 and len(i.liberties or [])==1:
            self.detect_ko(i, capture)

    def remove_stone(self, i):
        if type(i) is str:
            i = self.intersections[coord.from_xy(i)]
        # There is no checking for here unlike in add_stone
        i.color = None
        if i.group is not None:
            i._group.remove(i)
            #i.group.remove(i)
            #if len(i.group)==None:
            #    self.groups.remove(i.group)
            self.add_stone(i, None)
            # To handle correctly the groups of empty spots, toggle comments below
            #i.group = None
            #libg = map(self.group, i.liberties)
            #if len(libg):
            #    i.group = reduce(lambda a, b: a.merge(b) or a, libg)
            #else:
            #    i.group = group()
            #    i.group.add(i)

    def __str__(self):
        rows = [ term.NORMAL+u"%2s "%coord.Y(x) for x in xrange(self.size) ]
        rows += [ term.NORMAL+'   '+u''.join([ "%2s"%coord.X(x) for x in xrange(self.size) ]) ]
        rows += [ u"Prisoners : White(%i) Black(%i)"%(self.prisoners[WHITE], self.prisoners[BLACK]) ]
        for x, y in iterate_coords(self.size):
            rows[y] += ' '+self.intersections[x, y].prettyprint(False)
        return (term.NORMAL+u'\n').join(rows)

    def hilite(self, hilite=[]):
        rows = [ term.NORMAL+u"%2s "%coord.Y(x) for x in xrange(self.size) ]
        rows += [ term.NORMAL+'   '+u''.join([ "%2s"%coord.X(x) for x in xrange(self.size) ]) ]
        rows += [ u"Prisoners : White(%i) Black(%i)"%(self.prisoners[WHITE], self.prisoners[BLACK]) ]
        for x, y in iterate_coords(self.size):
            i = self.intersections[x, y]
            rows[y] += ' '+i.prettyprint(i in hilite)
        return (term.NORMAL+u'\n').join(rows)

    def dump(self, hilite=[]):
        print unicode(self.hilite(hilite or []))


    def add_pass(self):
        pass    # haha

    feed = feed         # explicit is better they say, this way of embedding out-of-class definitions is dirty at the very least.
    black = property(lambda self: group((b for b in self.intersections.values() if b.color is BLACK)))
    white = property(lambda self: group((w for w in self.intersections.values() if w.color is WHITE)))
    def fuzzy_groups(self):
        stones = { BLACK:self.black, WHITE:self.white }
        ret = { WHITE: set(), BLACK: set() }
        for c in (WHITE, BLACK):
            S = stones[c].copy() # set of stones
            while len(S)>0:
                s = S.pop()
                sg = fuzzy_group(s.group)
                ret[c].add(sg)
                S.difference_update(sg)
        return ret
    



neighbours_in_set = lambda i, s: group(set((n for n in i.neighbours if n not in i)).intersection(s))










def dead_groups(g):
    def has_backup(grp):
        friend_liberties = [len(gr.liberties.difference(x.liberties)) for gr in x.liberties.surrounding_groups if gr is not x and gr.color is x.color]
        return reduce(int.__add__, friend_liberties, 0) > 2
    def is_behind_in_semeai(grp):
        return reduce(lambda a, b: a and b, [len(sg.liberties)>len(x.liberties) for sg in x.surrounding_groups], x.surrounding_groups)
    def is_alive(grp):
        return has_backup(grp) or not is_behind_in_semeai(grp)
    dead = [ x for x in g.groups if not is_alive(x) ]
    return dead

def show_dead_groups(g):
    g.dump(reduce(lambda a, b: a.update(b) or a, dead_groups(g), set()))

def remove_dead_groups(g):
    to_remove = []
    for grp in dead_groups(g):
        g.prisoners[grp.color is BLACK and WHITE or BLACK] += len(grp)
        for s in grp:
            to_remove.append(s)
    for s in to_remove:
        g.remove_stone(s)


def fuzzy_group(a):
    ga = group()
    if a.color is None:
        return ga
    count = -1
    cur = a
#    print ">>>>>>>>>", a
    while count!=len(ga):
#        print len(ga), count
        count=len(ga)
        al = cur.liberties
        n2n3 = al.neighbours.union(al.liberties.neighbours)
        n = reduce(lambda a, b: a.update(b) or a,
                   (x.group for x in n2n3 if x not in a and x.color is a.color), group())
        ga.update(n)
        cur = n
#    print ">>>>>>>>>", a, ga
    return ga



def find_territory_seeds(g):
    b = g.black
    w = g.white
    s = b.union(w)
    gbl = b.liberties
    gwl = w.liberties
    bseeds = group(filter(lambda x: reduce(lambda a, b: a and b.color in (None, BLACK), x.neighbours, True), gbl))
    wseeds = group(filter(lambda x: reduce(lambda a, b: a and b.color in (None, WHITE), x.neighbours, True), gwl))
    bterr = group(bseeds)
    wterr = group(wseeds)
    while bseeds or wseeds:
        bseeds = group((n for x in bseeds for n in x.neighbours if n not in bterr and n not in wterr and n not in s))
        wseeds = group((n for x in wseeds for n in x.neighbours if n not in wterr and n not in bterr and n not in s))
        bterr.update(bseeds)
        wterr.update(wseeds)

    wterr.update(g.white)
    bterr.update(g.black)
    bfrontier = group(( x for x in bterr if x not in b and filter(lambda n: n in wterr, x.neighbours) ))
    wfrontier = group(( x for x in wterr if x not in w and filter(lambda n: n in bterr, x.neighbours) ))
    bterr.difference_update(bfrontier)
    wterr.difference_update(wfrontier)

    #print "black has", bterr
    #print "white has", bterr
    # remove all seeds with ONE good neighbour
    #bterr = filter(lambda x : 2>reduce(lambda a, b: (b.color is BLACK or b in bterr) and (a+1) or (a), x.neighbours, 0), bterr)
    #wterr = filter(lambda x : 2>reduce(lambda a, b: (b.color is WHITE or b in wterr) and (a+1) or (a), x.neighbours, 0), wterr)
    #print sorted(wterr)
    return { WHITE:  wterr, BLACK: bterr }
        

def estimate_score(g, do_dump=False):
    # implements chinese counting
    #p = g.fork()
    p = position(g.size)
    p.data = g.current.data
    backup = g.current
    g.current = p
    # the dead groups are meaningless (they count as "less alive stones on the board")
    remove_dead_groups(g)
    all_groups = g.fuzzy_groups()
    # floodfill by looping over "territory seeds", ie liberties that are not shared with an enemy group
    terr = find_territory_seeds(g)

    dead_black = [ dead for dead in all_groups[BLACK] if 5>len(neighbours_in_set(dead, terr[BLACK])) ]
    dead_white = [ dead for dead in all_groups[WHITE] if 5>len(neighbours_in_set(dead, terr[WHITE])) ]

    if len(dead_black)>0 or len(dead_white)>0:
        for d in dead_black:
            for s in d:
                s.color = None
        for d in dead_white:
            for s in d:
                s.color = None
        all_groups = g.fuzzy_groups()
        # floodfill by looping over "territory seeds", ie liberties that are not shared with an enemy group
        terr = find_territory_seeds(g)

        dead_black = [ dead for dead in all_groups[BLACK] if 5>len(neighbours_in_set(dead, terr[BLACK])) ]
        dead_white = [ dead for dead in all_groups[WHITE] if 5>len(neighbours_in_set(dead, terr[WHITE])) ]


    for color in (WHITE, BLACK):
        for s in terr[color]:
            s.color = color


    # now count
    score = { WHITE: len(terr[WHITE])+g.komi, BLACK: len(terr[BLACK]) }
#    for i in g.intersections.values():
#        if i.color in (WHITE, BLACK):
#            score[i.color]+=1

    #print "White has :"
    #g.dump(terr[WHITE])
    #print "Black has :"
    #g.dump(terr[BLACK])
    do_dump and g.dump()
    g.current = backup
    return score, terr


def aftermove(c) :
#    print unicode(c)
#    grp = { WHITE:[], BLACK:[], None:[] }
#    for g in c.groups:
#        grp[g.color].append(g)
#    print grp
#    sys.stdin.read(1)
    pass


def hilite(g, *x):
    print unicode(g.hilite(reduce(lambda a,b:a.update(b) or a, x, set())))


# choix de coup :
#   max de fonction_evaluation(fonction_strategie(position), position) pour coup suivant
# c'est mal dit : fonction_strategie(position) renvoie la fonction d'evaluation
#   coup max de fonction_strategie(position)(position) ?
# ca a l'air encore plus mal dit

if __name__=='__main__':
    set_palette(vga_palette)
    #g = goban(19)
    #print unicode(g)
    #g.add_stone(g.intersections[3, 3], BLACK)
    #g.add_stone(g.intersections[3, 4], BLACK)
    #print unicode(g)
    #print g.intersections[3, 3].group
    #print g.intersections[3, 4].group
    #g.remove_stone(g.intersections[3, 4])
    #print unicode(g)
    #print g.intersections[3, 3].group
    #test_data = open('../2010-03-07-Blanc-Noir.sgf').read()
    test_data = open('../sgf/blob-gnugo.sgf').read()
    #test_data = open('../Murakawa-Iyama-9x9.sgf').read()
    g=goban()
    col = SGFParser(test_data).parse()
    g.feed(col[0].mainline(), aftermove)
    print unicode(g)
    print estimate_score(g)

