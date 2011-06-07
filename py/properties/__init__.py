
__all__ = [ "property_container", "properties" ]

from utils import cached_property

class property_container(object):
    def __init__(self):
        self.v = {}    # for cached_property
        self.ref = {}    # for cached_property

def update(cls, p):
    print p
    for pn in p:
        print pn
        cls.__setattr__(pn, cached_property(*p[pn]))


class properties(type):
    properties = {
        'intersection': {},
        'goban': {},
        'grid_system':{},
        'group': {}
    }
    def __init__(cls, name, bases, dic):
        print "pouet", name, properties.properties[name]
        def nil(s, *a, **b):
            pass
        orig = '__init__' in dic and dic['__init__'] or nil
        def init(self, *args, **kw):
            orig(self, *args, **kw)
            update(self, properties.properties[name])
        dic['__init__'] = init
        cls.__init__ = init
        return type.__init__(cls, name, bases, dic)


