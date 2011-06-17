# -*- coding: utf-8 -*-
__all__ = [ "WEST", "NORTH", "SOUTH", "EAST", "NORTHWEST", "NORTHEAST", "SOUTHWEST", "SOUTHEAST", "UNDEF", "direction" ]

from utils import *

WEST = u'←'
NORTH = u'↑'
SOUTH = u'↓'
EAST = u'→'
NORTHWEST = u'↖'
NORTHEAST = u'↗'
SOUTHWEST = u'↙'
SOUTHEAST = u'↘'
UNDEF = u'↺'

dir2ascii = {
    WEST: 'WEST',
    NORTH: 'NORTH',
    SOUTH: 'SOUTH',
    EAST: 'EAST',
    NORTHWEST: 'NORTHWEST',
    NORTHEAST: 'NORTHEAST',
    SOUTHWEST: 'SOUTHWEST',
    SOUTHEAST: 'SOUTHEAST',
    UNDEF: 'UNDEF',
}

direction_add_table = {
    (EAST, UNDEF): EAST,
    (WEST, UNDEF): WEST,
    (NORTH, UNDEF): NORTH,
    (SOUTH, UNDEF): SOUTH,
    (NORTHWEST, UNDEF): NORTHWEST,
    (NORTHEAST, UNDEF): NORTHEAST,
    (SOUTHWEST, UNDEF): SOUTHWEST,
    (SOUTHEAST, UNDEF): SOUTHEAST,
    (UNDEF, EAST): EAST,
    (UNDEF, WEST): WEST,
    (UNDEF, NORTH): NORTH,
    (UNDEF, SOUTH): SOUTH,
    (UNDEF, NORTHWEST): NORTHWEST,
    (UNDEF, NORTHEAST): NORTHEAST,
    (UNDEF, SOUTHWEST): SOUTHWEST,
    (UNDEF, SOUTHEAST): SOUTHEAST,

    (WEST, NORTH): NORTHWEST,
    (EAST, NORTH): NORTHEAST,
    (WEST, SOUTH): SOUTHWEST,
    (EAST, SOUTH): SOUTHEAST,
    (NORTH, WEST): NORTHWEST,
    (NORTH, EAST): NORTHEAST,
    (SOUTH, WEST): SOUTHWEST,
    (SOUTH, EAST): SOUTHEAST,

    (WEST, NORTHWEST): NORTHWEST,
    (EAST, NORTHWEST): NORTH,
    (NORTH, NORTHWEST): NORTHWEST,
    (SOUTH, NORTHWEST): WEST,

    (WEST, NORTHEAST): NORTH,
    (EAST, NORTHEAST): NORTHEAST,
    (NORTH, NORTHEAST): NORTHEAST,
    (SOUTH, NORTHEAST): EAST,

    (WEST, SOUTHWEST): SOUTHWEST,
    (EAST, SOUTHWEST): SOUTH,
    (SOUTH, SOUTHWEST): SOUTHWEST,
    (NORTH, SOUTHWEST): WEST,

    (WEST, SOUTHEAST): SOUTH,
    (EAST, SOUTHEAST): SOUTHEAST,
    (SOUTH, SOUTHEAST): SOUTHEAST,
    (NORTH, SOUTHEAST): EAST,

    (NORTHWEST, WEST): NORTHWEST,
    (NORTHWEST, EAST): NORTH,
    (NORTHWEST, NORTH): NORTHWEST,
    (NORTHWEST, SOUTH): WEST,

    (NORTHEAST, WEST): NORTH,
    (NORTHEAST, EAST): NORTHEAST,
    (NORTHEAST, NORTH): NORTHEAST,
    (NORTHEAST, SOUTH): EAST,

    (SOUTHWEST, WEST): SOUTHWEST,
    (SOUTHWEST, EAST): SOUTH,
    (SOUTHWEST, SOUTH): SOUTHWEST,
    (SOUTHWEST, NORTH): WEST,

    (SOUTHEAST, WEST): SOUTH,
    (SOUTHEAST, EAST): SOUTHEAST,
    (SOUTHEAST, SOUTH): SOUTHEAST,
    (SOUTHEAST, NORTH): EAST,

    (NORTHWEST, NORTHEAST): NORTH,
    (NORTHWEST, SOUTHWEST): WEST,
    (NORTHEAST, NORTHWEST): NORTH,
    (NORTHEAST, SOUTHEAST): EAST,

    (SOUTHWEST, SOUTHEAST): SOUTH,
    (SOUTHWEST, NORTHWEST): WEST,
    (SOUTHEAST, SOUTHWEST): SOUTH,
    (SOUTHEAST, NORTHEAST): EAST,

}

color_merge = {
    (WHITE, BLACK): None,
    (BLACK, WHITE): None,
    (WHITE, WHITE): WHITE,
    (BLACK, BLACK): BLACK,
    (WHITE, None): WHITE,
    (BLACK, None): BLACK,
    (None, WHITE): WHITE,
    (None, BLACK): BLACK,
    (None, None): None,
}


class direction(object):
    threshold = 0.01
    def __init__(self, v=UNDEF, color_=0.):
        self.value = v
        if type(color_) is str:
            self.color_ = (color_==BLACK and 1.) or (color_==WHITE and -1.)
        else:
            self.color_ = float(color_)
    def __str__(self):
        return dir2ascii[self.value]+'('+str(self.color_)+')'
    def __repr__(self):
        return dir2ascii[self.value]+'('+str(self.color_)+')'
    def __unicode__(self):
        return self.value
    color = property(lambda self:
                         (self.color_ < -direction.threshold) and WHITE
                             or
                         (self.color_ > direction.threshold) and BLACK
                             or
                         None)
    def __eq__(self, d):
        return self.value is d.value and self.color is d.color
    def __add__(self, d):
        if type(d) is str:
            d = direction(d)
        ret = direction()
        if self.value is d.value:
            ret.value = self.value
        else:
            k = (self.value, d.value)
            ret.value = k in direction_add_table and direction_add_table[k] or UNDEF
        #ret.color = color_merge[self.color, d.color]
        ret.color_ = self.color_+d.color_
        return ret
    def __div__(self, d):
        return direction(self.value, self.color_/d)
    def __mul__(self, d):
        return direction(self.value, self.color_*d)


