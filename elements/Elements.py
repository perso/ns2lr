class Entity(object):

    def __init__(self, classname):
        self.classname = classname

class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Vertex(Point):
    def __init__(self, x, y, z, has_smoothing):
        super(Vertex, self).__init__(x, y, z)
        self.has_smoothing = has_smoothing