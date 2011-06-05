# -*- coding: utf-8 -*-
import sys

from sgflib import SGFParser, GameTreeEndError

from utils import *
from grid import *
from goban import *
from colorterm import *






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
				print coord(x, y),
				if x==y and x>=self.size:
					self.add_pass()
				else:
					#print "new stone", colors[col], coord(x, y)
					self.add_stone(self.intersections[x, y], colors[col])
				self.commit_position()
				aftermove(self)



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
#		if liberties_total==0:
#			raise IllegalMove("suicide")
		cap_count = 0
		capture = None
		if color and E:
			# check for a direct ko situation
#			if len(E)==1 and len(E[0])==1 and i.liberties is None:
#				self.active_ko = min(E[0])
#				self.active_ko.active_ko = True
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
		pass	# haha

	feed = feed		 # explicit is better they say, this way of embedding out-of-class definitions is dirty at the very least.
	black = cached_property(lambda self: group(self, (b for b in self.intersections.values() if b.color is BLACK)))
	white = cached_property(lambda self: group(self, (w for w in self.intersections.values() if w.color is WHITE)))
	def _fuzzy_groups(self):
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
	fuzzy_groups = cached_property(_fuzzy_groups)



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
#	for i in g.intersections.values():
#		if i.color in (WHITE, BLACK):
#			score[i.color]+=1

	#print "White has :"
	#g.dump(terr[WHITE])
	#print "Black has :"
	#g.dump(terr[BLACK])
	do_dump and g.dump()
	g.current = backup
	return score, terr


def aftermove(c) :
#	print unicode(c)
#	grp = { WHITE:[], BLACK:[], None:[] }
#	for g in c.groups:
#		grp[g.color].append(g)
#	print grp
#	sys.stdin.read(1)
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

