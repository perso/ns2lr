import ctypes


class SparkDataBlock(object):

    def __init__(self):
        pass

    def dump(self):
        raise NotImplementedError()

    def load(self):
        raise NotImplementedError()

class Entity(SparkDataBlock):

    def __init__(self, classname):
        self.classname = classname
        self.groupid = -1
        self.layerdata = {}
        self.properties = {}

class Vertex(SparkDataBlock):

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.has_smoothing = False

class Edge(SparkDataBlock):

    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2
        self.is_flipped = False

class Group(SparkDataBlock):

    def __init__(self, group_id, group_name):
        self.id = group_id
        self.name = group_name
        self.color = None
        self.is_visible = True

class EdgeLoop(SparkDataBlock):

    def __init__(self):
        self.edges = []

    def add_edge(self, edge):
        self.edges.append(edge)

class Face(SparkDataBlock):

    def __init__(self, border_edgeloop):
        self.scale = (1.0, 1.0)
        self.offset = (0.0, 0.0)
        self.angle = 0.0
        self.border_edgeloop = border_edgeloop
        self.edgeloops = []
        self.mapping_group_id = -1
        self.material = ""

class Triangle(SparkDataBlock):

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

class Material(SparkDataBlock):

    def __init__(self):
        self.chunk_id = 4

    def dump(self):
        b_repr = b""
        b_repr += ctypes.c_uint32(chunk_id)
        b_repr += ctypes.c_uint32(chunk_length)
        b_repr += ctypes.c_uint32(num_materials)
        b_repr += ctypes.c_uint32(material_filepath_length)
        b_repr += material_filepath.encode("utf-8")
        return b_repr

    def load(self):
        pass