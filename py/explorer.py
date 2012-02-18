from goban import IllegalMove
from utils import *
from grid import *

class explorer(object):
    CONTINUE = object()
    def __init__(self, grid, maxdepth=400):
        self.grid = grid
        self.maxdepth = maxdepth
        self.cache = {}
    def play_one(self, color, pos):
        self.grid.commit_position()
        self.grid.add_stone(pos, color)
    def go_back(self):
        self.grid.go_back()
    def explore(self, colP, colO, msP, msO, combP, combO, evP, evO, indent=0):
        if self.grid.current.data in self.cache:
            return self.cache[self.grid.current.data], []
        if indent>self.maxdepth:
            return None, []
        status = evP()
        outcomes = None
        tree = []
        if status is explorer.CONTINUE:
            outcomes = []
            for move in msP():
                #print '  '*indent, colP, move
                try:
                    self.play_one(colP, move)
                    result, moves = self.explore(colO, colP, msO, msP, combO, combP, evO, evP, indent+1)
                    outcomes.append(result)
                    tree.append((move, result, moves))
                except IllegalMove, im:
                    #self.grid.delete_position(self.grid.current)
                    continue
                self.go_back()
            status = combP(outcomes)
        #print '  '*indent, "=>", status
        if status is not explorer.CONTINUE:
            self.cache[self.grid.current.data] = status
        return status, tree


def shicho_works(victim):
    victim = min(victim.group)
    if victim.color is None or len(victim.group.liberties)>2:
        return (False, None)
    #exp = victim.grid.fork()
    colO = victim.color
    colP = colO is WHITE and BLACK or WHITE
    def evP():
        l=len(victim.group.liberties)
        print "evP", l, victim.group.liberties
        if l<=1:
            return True
        if l>2:
            return False
        return explorer.CONTINUE
    def evO():
        return explorer.CONTINUE
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
    deep = lambda x: type(x) is tuple and deep(x[1]) or x
    combP = lambda l: reduce(lambda a, b: a or deep(b), l, False)
    combO = lambda l: reduce(lambda a, b: a and deep(b), l, True)
    ret = explorer(victim.grid).explore(colP, colO, msP, msO, combP, combO, evP, evO)
    #victim.grid.delete_position(exp)
    return ret


