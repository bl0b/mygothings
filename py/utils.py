# -*- coding: utf-8 -*-
__all__ = ( 'xzip', 'iterate_box', 'iterate_coords', 'WHITE', 'BLACK', 'HOSHI', 'KO', 'term', 'cached_property', 'chrono', 'crawl' )

from colorterm import *
from time import time

       
class chrono(object):
    def __init__(self):
        self.t = time()
    def __float__(self):
        return time()-self.t
    def start(self):
        self.t = time()
    def stop(self):
        return float(self)

WHITE='w'
BLACK='b'
HOSHI='h'
KO='k'


def xzip(*a):
    i = [ iter(x) for x in a ]
    while True:
        yield [ x.next() for x in i ]



def iterate_box(x1, y1, x2, y2):
	return ( (x, y) for x in xrange(x1, x2+1) for y in xrange(y1, y2+1) )

def iterate_coords(size):
	return ( (x, y) for x in xrange(size) for y in xrange(size) )


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


class cached_property(property):
	def __init__(self, fget, fset=None):
		#self.ref=None
		#self.v=None
		def _g(x):
			d = x.grid.current.data
			if d!=(self in x.ref and x.ref[self] or None):
				x.ref[self] = d
				x.v[self] = fget(x)
			return x.v[self]
		def _s(x, value):
			fset(x, value)
			x.v[self] = value
			x.ref[self] = x.grid.current.data
		property.__init__(self, _g, fset is not None and _s or None)
		#property.__init__(self, fget, fset)


import pygame
from pygame.locals import *

def crawl(G, root, hl = lambda g: None):
    pygame.init()
    done = False
    backup = G.current
    G.current = root
    refresh = True
    while not done:
        if refresh:
            G.dump(hl(G))
            refresh = False
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        #print keys, '\r',
        if keys[K_ESCAPE]:
            done = True
        elif keys[K_UP]:
            G.next_variation()
            refresh = True
        elif keys[K_DOWN]:
            G.previous_variation()
            refresh = True
        elif keys[K_LEFT]:
            G.go_back()
            refresh = True
        elif keys[K_RIGHT]:
            G.go_forward()
            refresh = True
    G.current = backup

