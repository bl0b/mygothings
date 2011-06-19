# -*- coding: utf-8 -*-
__all__ = ( 'IllegalMove', 'goban' )

import sys

from sgflib import SGFParser, GameTreeEndError

from utils import *
from grid import *

from properties import *





class IllegalMove(Exception) :
    pass


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
                print coord(self, x, y),
                if x==y and x>=self.size:
                    self.add_pass()
                else:
                    #print "new stone", colors[col], coord(self, x, y)
                    self.add_stone(self.intersections[coord(self, x, y).xy], colors[col])
                self.commit_position()
                aftermove(self)



class goban(grid_system):
    def __init__(self, size=None):
        grid_system.__init__(self, type(size) is int and size or None)
        if type(size) is str:
            self.feed(SGFParser(open(size).read()).parse()[0].mainline())
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
        return filter(is_legal_move, self.intersections.values())
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
                #		if liberties_total==0:
                    #			raise IllegalMove("suicide")
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
            i._group=group(self)
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
            self.add_stone(i, None)

    def __str__(self):
        rows = [ term.NORMAL+'   '+u''.join([ "%2s"%coord.X(x) for x in xrange(self.size) ]) ]
        rows += [ term.NORMAL+u"%2s "%coord.Y(x) for x in xrange(self.size) ]
        rows.reverse()
        rows += [ u"Prisoners : White(%i) Black(%i)"%(self.prisoners[WHITE], self.prisoners[BLACK]) ]
        for x, y in iterate_coords(self.size):
            rows[y] += ' '+self.intersections[coord(self, x, y).xy].prettyprint(False)
        return (term.NORMAL+u'\n').join(rows)

    def hilite(self, hilite=[]):
        rows = [ term.NORMAL+'   '+u''.join([ "%2s"%coord.X(x) for x in xrange(self.size) ]) ]
        rows += [ term.NORMAL+u"%2s "%coord.Y(x) for x in xrange(self.size) ]
        rows.reverse()
        rows += [ u"Prisoners : White(%i) Black(%i)"%(self.prisoners[WHITE], self.prisoners[BLACK]) ]
        for x, y in iterate_coords(self.size):
            i = self.intersections[coord(self, x, y).xy]
            rows[y] += ' '+i.prettyprint(i in hilite)
        return (term.NORMAL+u'\n').join(rows)

    def hilitevec(self, hilite=[]):
        #hlpos = set([ x[0] for x in hilite ])
        hlvec = dict(hilite)
        rows = [ term.NORMAL+'   '+u''.join([ "%2s"%coord.X(x) for x in xrange(self.size) ]) ]
        rows += [ term.NORMAL+u"%2s "%coord.Y(x) for x in xrange(self.size) ]
        rows.reverse()
        rows += [ u"Prisoners : White(%i) Black(%i)"%(self.prisoners[WHITE], self.prisoners[BLACK]) ]
        for x, y in iterate_coords(self.size):
            i = self.intersections[coord(self, x, y).xy]
            if i in hlvec:
                rows[y] += ' '+i.prettyprint(True, hlvec[i])
            else:
                rows[y] += ' '+i.prettyprint(False)
        return (term.NORMAL+u'\n').join(rows)

    def dump(self, hilite=[]):
        if type(hilite) is dict:
            print unicode(self.hilitevec(hilite.items()))
        else:
            print unicode(self.hilite(hilite or []))


    def add_pass(self):
        pass    # haha

    feed = feed         # explicit is better they say, this way of embedding out-of-class definitions is dirty at the very least.
    black = cached_property(lambda self: group(self, (b for b in self.intersections.values() if b.color is BLACK)))
    white = cached_property(lambda self: group(self, (w for w in self.intersections.values() if w.color is WHITE)))
    def _fuzzy_groups(self):
        stones = { BLACK:self.black, WHITE:self.white }
        ret = { WHITE: set(), BLACK: set() }
        for c in (WHITE, BLACK):
            S = stones[c].copy() # set of stones
            while len(S)>0:
                s = S.pop()
                #print "computing fuzzy_group from", s
                #sg = fuzzy_group(s.group)
                sg = s.group.fuzzy_group
                sg.update(s.group)
                #print "                => ", sg, s in sg
                ret[c].add(sg)
                S.difference_update(sg)
        return ret
    fuzzy_groups = cached_property(_fuzzy_groups)
    # hack getattribute to retrieve an intersection more easily.
    # with g = goban(),
    # g['s15'] can be written g.s15
    def __getitem__(self, *xy):
        c = coord(self, *xy)
        c.y = self.size-1-c.y
        return self.intersections[c.xy]
    def __setitem__(self, *xy):
        value = xy.pop()
        c = coord(self, *xy)
        c.y = self.size-1-c.y
        self.intersections[c.xy] = value
    def __getattribute__(self, attr):
        if coord.match(attr):
            try:
                return self[attr]
            except KeyError, ke:
                print "requesting attribute", attr, "..."
                raise ke
        return object.__getattribute__(self, attr)

