# -*- coding: utf-8 -*-
__all__ = ( 'fuzzy_group', 'grid_item', 'intersection', 'group', 'coord', 'position', 'grid_system' )

from utils import *

# Define the goban as a graph


class grid_item(object):
	def __init__(self, grid):
		self.grid = grid
		self.v = {}	# for cached_property
		self.ref = {}	# for cached_property


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
	group = property(compute_grp, lambda s, x: x)




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

def fuzzy_group(a):
	ga = group(a.grid, a)
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



class group(set, grid_item):
	def __init__(self, grid, _set=None):
		if _set is not None:
			set.__init__(self, _set)
		else:
			set.__init__(self)
		grid_item.__init__(self, grid)
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
	groups = cached_property(lambda self: list(set([ x.group for x in self.intersections.values() if x.color ])))
	territories = cached_property(lambda self: list(set([ x.group for x in self.intersections.values() if not x.color ])))
	def merge_groups(self, g1, g2):
		g1.merge(g2)
		return g1
#	def remove_from_group(self, g, s):
#		g.remove(s)
#		if len(g)==0:
#			try:
#				self.groups.remove(g)
#			except ValueError, ve:
#				pass

