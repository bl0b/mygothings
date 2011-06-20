# -*- coding: utf-8 -*-
import startup # enables history persistance
import sys
sys.ps1='> '
sys.ps2=''


from sgflib import SGFParser, GameTreeEndError

from utils import *
from grid import *
from goban import *
from colorterm import *

from direction import *
from shape import *



def fuzzy_2(x):
    last=0
    ga = x.group
    while len(ga)!=last:
        last = len(ga)
        ga = group_union(x.grid, (n.group for n in area(ga).neighbours if n.color is x.color))
    return ga


def fuzz(i):
    return group_union(i.grid, (x.group for x in area(i).neighbours if x.color is i.color))

def rec_fuzz(grp):
    f = fuzz(grp)
    #f = fuzz(grp)
    print f, grp
    if len(f)>len(grp):
        #print 'F', f
        #print 'R', grp
        return rec_fuzz(f)
    else:
        return grp

def toplevel_contexts(g):
    #ret = set()
    ret = []
    S = g.black+g.white
    while len(S)>0:
        s = min(S)
        f = rec_fuzz(s.group)
        S.difference_update(f)
        #ret.add(f)
        ret.append(f)
    return ret

        


def field_diff(g, col):
        f = clean_vs(g)
        return reduce(lambda a, b: a+b.color_, f.values(), 0.)
        #own, foe = reduce(lambda a, b: (a[0]+(f[b].color is col and 1 or 0), a[1]+(f[b].color not in (col, None) and 1 or 0)), f, (0, 0))
        #return own-foe

lmscore = lambda col: reduce(lambda a, b: b[1]>a[1] and b or a, ((m, try_move(g, m, col)) for m in g.legal_moves(col)))
lmscores = lambda col: sorted([(m, try_move(g, m, col)) for m in g.legal_moves(col)], lambda a, b: a[1]>=b[1])

def next_move(col):
    g.commit_position()
    lms = lmscore(col)
    print lms
    g.add_stone(lms[0], col)
    g.dump()


def try_move(g, m, c):
    p=g.current
    g.current = position(g.size)
    g.current.data = long(p.data)
    try:
        g.add_stone(m, c)
        ret = field_diff(g, c)
        g.current = p
        return ret
    except IllegalMove, im:
        g.current = p
        return -1000


def compute_vs(g):
    vs = g.vspace()
    sqrtsz = (g.size**.5)-1
    polynom = lambda x: x<=sqrtsz and .1**(sqrtsz-x) or 1./(1.+(x-sqrtsz))
    ll=[(l, direction(s.n2o(l), grp.color)) for grp in g.groups for s in grp for l in s.liberties]
    for x in xrange(2):
        #print ll
        for i, d in ll:
            h = (i.heightx+i.heighty)*.5
            vs[i] = vs[i]+d*polynom(h)
        ll = [ (n, d) for i, d in ll for n in i.o2n(d.value) if n.color is None ]
    return vs


def clean_vs(g):
    vs = g.vspace()
    v2 = compute_vs(g)
    for k in xrange(2):
        for i in vs:
            vs[i]=v2[i]
        for i in v2:
            v2[i] = reduce(direction.__add__, (vs[n]/2 for n in i.neighbours if n.color is None), direction())
    return v2





neighbours_in_set = lambda i, s: group(i.grid, set((n for n in i.neighbours if n not in i)).intersection(s))



c_ = { WHITE: BLACK, BLACK:WHITE }
c = WHITE
def play(*pos):
    global c
    for p in pos:
        c = c_[c]
        g.add_stone(g[p], c)
    

#area = lambda i: reduce(lambda a, b: a.update(b) or a, i.group.nth_neighbours_iter(lambda x: x.color in (None, i.color)), group(i.grid))
def iscore(c, b):
    if b.color is None:
        return 0
    elif b.color is c:
        return 1
    else:
        return -1

neighbour_score = lambda i, c: reduce(lambda a, b: a+iscore(c, b), i.neighbours, 0) 
area = lambda i: reduce(lambda a, b: a.update(b) or a,
                        i.group.nth_neighbours_iter(lambda x: x.color is None,
                                                    lambda x: x.color is None and neighbour_score(x, i.color)>=0),
                        group(i.grid))

def influence_field(g):
    f = {}
    for i in g.intersections.values():
        f[i] = { WHITE:0, BLACK:0 }
    #print g.groups
    for grp in g.groups:
        #print grp
        for i in area(grp):
            f[i][grp.color] += 1
    return f

def influence(g):
    f = influence_field(g)
    ret = {
        'B': group(g),
        'W': group(g),
        'Z': group(g),
        'E': group(g),
        'CW': group(g),
        'CB': group(g),
    }
    for i in g.intersections.values():
        x = f[i]
        print x
        if 0==x[BLACK]==x[WHITE]:
            ret['Z'].add(i)
        elif x[BLACK]==x[WHITE]:
            ret['E'].add(i)
        elif x[WHITE]==0:
            ret['B'].add(i)
        elif x[BLACK]==0:
            ret['W'].add(i)
        elif x[BLACK]>x[WHITE]:
            ret['CB'].add(i)
        elif x[WHITE]>x[BLACK]:
            ret['CW'].add(i)
        else:
            raise ValueError(i)
    return ret


class context(object):
    def __init__(self, x):
        x = x.group
        a = area(x)
        n = a.surrounding_groups
        n.difference_update([x])
        n.update((xn.group for xn in x.neighbours))
        self.area = a
        self.neighbours = n
    def __str__(self):
        return 'area: '+str(len(self.area))+', neighbours: '+str([ (n.color, len(n.liberties)) for n in self.neighbours])



def toggle_color(c):
    if c is BLACK:
        return WHITE
    elif c is WHITE:
        return BLACK
    else:
        return c


class explorer(object):
    __doc__="stamp"
    CONTINUE = object()
    def __init__(self, grid):
        self.grid = grid
    def play_one(self, color, pos):
        self.grid.commit_position()
        self.grid.add_stone(pos, color)
    def go_back(self):
        self.grid.go_back()
    def explore(self, colP, colO, msP, msO, combP, combO, evP, evO, indent=0):
        status = evP()
        outcomes = None
        if status is explorer.CONTINUE:
            outcomes = []
            for move in msP():
                #print '  '*indent, colP, move
                self.play_one(colP, move)
                outcomes.append(self.explore(colO, colP, msO, msP, combO, combP, evO, evP, indent+1))
                self.go_back()
            status = combP(outcomes)
        #print '  '*indent, "=>", status
        return outcomes and status or colP


def shicho_works(victim):
    victim = min(victim.group)
    if victim.color is None or len(victim.group.liberties)>2:
        return (False, None)
    exp = victim.grid.fork()
    colO = victim.color
    colP = colO is WHITE and BLACK or WHITE
    def status():
        if victim.color is None or len(victim.group.liberties)==0:
            return True
        if len(victim.group.liberties)>2:
            return False
        return explorer.CONTINUE
    evP = status
    evO = status
    def msP():
        return victim.group.liberties
    def msO():
        ret = group_union(victim.grid, (n.liberties for n in victim.group.neighbours if n.color not in (None, victim.color) and len(n.group.liberties)<2))
        ret.update(victim.group.liberties)
        return ret
    combP = lambda l: reduce(lambda a, b: a or b, l, False)
    combO = lambda l: reduce(lambda a, b: a and b, l, True)
    ret = explorer(victim.grid).explore(colP, colO, msP, msO, combP, combO, evP, evO)
    #victim.grid.delete_position(exp)
    return ret, exp



def is_capturable(victim):
    "brute-force check of at least one possibility to capture the victim group, limited to groups under 10 liberties."
    victim = min(victim.group)
    if victim.color is None or len(victim.group.liberties)>10:
        return (False, None)
    exp = victim.grid.fork()
    colO = victim.color
    colP = colO is WHITE and BLACK or WHITE
    def status():
        if victim.color is None or len(victim.group.liberties)==0:
            return True
        if len(victim.group.liberties)>10:
            return False
        return explorer.CONTINUE
    evP = status
    evO = status
    def msP():
        return victim.group.liberties
    def msO():
        ret = group_union(victim.grid, (n.liberties for n in victim.group.neighbours if n.color not in (None, victim.color) and len(n.group.liberties)<2))
        ret.update(victim.group.liberties)
        return ret
    combP = lambda l: reduce(lambda a, b: a or b, l, False)
    combO = lambda l: reduce(lambda a, b: a and b, l, True)
    ret = explorer(victim.grid).explore(colP, colO, msP, msO, combP, combO, evP, evO)
    #victim.grid.delete_position(exp)
    return ret, exp



def detect_eyes(grp):
    return set((
            i.group for i in connex(area(grp))
                    if  len(set((n.color for n in i.neighbours)))==1
                    and reduce(lambda a, b: a and len(b.liberties)>1, i.surrounding_groups)
           ))



def all_neighbours(i):
    ng = {}
    dist = 1
    for grp in i.group.nth_neighbours_iter(lambda x: x.color is None):
        for x in (a.group for a in grp if a.color is not None):
            if x not in ng or ng[x]>dist:
                ng[x] = dist
        dist = dist+1
    return ng



def connex(S):
    return set(( x.group.intersection(S) for x in S ))


def group_union(grid, args):
    return reduce(lambda a, b: a.update(b) or a, args, group(grid))
        








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




def find_territory_seeds(g):
    b = g.black
    w = g.white
    s = b.union(w)
    gbl = b.liberties
    gwl = w.liberties
    bseeds = group(g, filter(lambda x: reduce(lambda a, b: a and b.color in (None, BLACK), x.neighbours, True), gbl))
    wseeds = group(g, filter(lambda x: reduce(lambda a, b: a and b.color in (None, WHITE), x.neighbours, True), gwl))
    bterr = group(g, bseeds)
    wterr = group(g, wseeds)
    while bseeds or wseeds:
        bseeds = group(g, (n for x in bseeds for n in x.neighbours if n not in bterr and n not in wterr and n not in s))
        wseeds = group(g, (n for x in wseeds for n in x.neighbours if n not in wterr and n not in bterr and n not in s))
        bterr.update(bseeds)
        wterr.update(wseeds)

    wterr.update(g.white)
    bterr.update(g.black)
    bfrontier = group(g, ( x for x in bterr if x not in b and filter(lambda n: n in wterr, x.neighbours) ))
    wfrontier = group(g, ( x for x in wterr if x not in w and filter(lambda n: n in bterr, x.neighbours) ))
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
    do_dump and g.dump()
    all_groups = g.fuzzy_groups
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
        do_dump and g.dump()
        all_groups = g.fuzzy_groups
        # floodfill by looping over "territory seeds", ie liberties that are not shared with an enemy group
        terr = find_territory_seeds(g)

        dead_black = [ dead for dead in all_groups[BLACK] if 5>len(neighbours_in_set(dead, terr[BLACK])) ]
        dead_white = [ dead for dead in all_groups[WHITE] if 5>len(neighbours_in_set(dead, terr[WHITE])) ]
        do_dump and g.dump(reduce(lambda a, b: a.update(b) or a, dead_black, group(g)))
        do_dump and g.dump(reduce(lambda a, b: a.update(b) or a, dead_white, group(g)))


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
    #test_data = open('../sgf/blob-gnugo.sgf').read()
    #test_data = open('../sgf/test.sgf').read()
    #test_data = open('../Murakawa-Iyama-9x9.sgf').read()
    #g=goban()
    #col = SGFParser(test_data).parse()
    #g.feed(col[0].mainline(), aftermove)
    #print
    #print unicode(g)
    #print estimate_score(g)

    #g=goban(9)
    #print lmscores(BLACK)

    g=goban('../sgf/goama134.sgf')

    st=shape_tree()
    st.from_strings(["sf", "fs"], 'crosscut')
    st.from_strings(["s.", "fs"], 'cutting_point')
    st.from_strings(["s!", "ss"], 'empty_triangle')
    st.from_strings(["ss", "!!", "ss"], 'bamboo_joint')
    stma = st.match_all(g)
    #print stma

    bad_shape = shape_tree()
    bad_shape.from_strings([".!.", "sfs", " f "], "tobi_tranche")
    bad_shape.from_strings(["...", "sf.", ".fs", "..."], "keima_tranche")
    bad_shape.from_strings(["s..", ".!.", "..s"], "elephant")
    bad_shape.from_strings(["s!", "Fs"], 'cutting_point')
    bad_shape.from_strings(["?  ", "s! ", "ss?"], 'empty_triangle')
    bad = bad_shape.match_all(g)

