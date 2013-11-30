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
    def __init__(self, x, y, z):
        super(Vertex, self).__init__(x, y, z)
        self.has_smoothing = False

class Edge(object):
    def __init__(self, vi_1, vi_2):
        self.vi_1 = vi_1
        self.vi_2 = vi_2
        self.is_flipped = False

class Group(object):
    def __init__(self, _id, _name):
        self.id = _id
        self.name = _name
        self.color = None
        self.is_visible = True

class EdgeLoop(object):

    def __init__(self):
        pass

    def add_edge(self, edge_index, is_flipped):
        self.edge_index = edge_index
        self.is_flipped = is_flipped

class Face(object):

    def __init__(self, edgeloop):
        self.edgeloop = edgeloop

class Triangle(object):

    def __init__(self, vi_1, vi_2, vi_3):
        self.vi_1 = vi_1
        self.vi_2 = vi_2
        self.vi_3 = vi_3
        self.sni_1 = 0
        self.sni_2 = 0
        self.sni_3 = 0

    def set_smoothed_normals(self, sni_1, sni_2, sni_3):
        self.sni_1 = sni_1
        self.sni_2 = sni_2
        self.sni_3 = sni_3
