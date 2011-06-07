# -*- coding: utf-8 -*-
import sys
sys.ps1='> '
sys.ps2=''


from sgflib import SGFParser, GameTreeEndError

from utils import *
from grid import *
from goban import *
from colorterm import *
from direction import *

shape_0 = 0
shape_1 = 10
shape_I = 20
shape_T = 30
shape_L = 40
shape_X = 50

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
    return sorted((shape_encoder[len(t)==2 and t or len(t)] for t in (tuple((s.n2o(x) for x in s.neighbours if x in grp)) for s in grp)))
    
def encode_shape_int(g, grp):
    return reduce(lambda a, b: a*10+b, encode_shape(g, grp))
    


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
    polynom = lambda x: x<=sqrtsz and 1./(1.+2*(sqrtsz-x)) or 1./(1.+.5*(x-sqrtsz))
    ll=[(l, direction(s.n2o(l), grp.color)) for grp in g.groups for s in grp for l in s.liberties]
    for x in xrange(1):
        #print ll
        for i, d in ll:
            h = i.heightx+i.heighty-i.min_height
            vs[i] = vs[i]+d*polynom(h)
            ll = [ (n, d) for i, d in ll for n in i.o2n(d.value) if n.color is None ]
    return vs


def clean_vs(g):
    vs = g.vspace()
    v2 = compute_vs(g)
    for k in xrange(4):
        for i in vs:
            vs[i]=v2[i]
        for i in v2:
            v2[i] = reduce(direction.__add__, (vs[n]/2 for n in i.neighbours if n.color is None), direction())
    return v2





neighbours_in_set = lambda i, s: group(i.grid, set((n for n in i.neighbours if n not in i)).intersection(s))










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
    g=goban(9)
    print lmscores(BLACK)

