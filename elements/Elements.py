class Entity(object):

    def __init__(self, classname):
        self.classname = classname
        self.groupid = -1
        self.layerdata = {}
        self.properties = {}

class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Vertex(Point):
    def __init__(self, x, y, z, has_smoothing):
        super(Vertex, self).__init__(x, y, z)
        self.has_smoothing = has_smoothing

class Group(object):
    def __init__(self, _id, _name):
        self.id = _id
        self.name = _name
        self.color = None
        self.is_visible = True