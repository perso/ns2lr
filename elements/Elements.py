import ctypes


class SparkDataBlock(object):

    def __init__(self):
        pass

    def write(self):
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

    def __init__(self, id, x=0.0, y=0.0, z=0.0, smoothing=False):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.smoothing = smoothing

    def write(self, stream):
        stream.write_float32(self.x)
        stream.write_float32(self.y)
        stream.write_float32(self.z)
        stream.write_unsigned_char8(self.smoothing)

    def load(self, stream):
        self.x = stream.read_float32()
        self.y = stream.read_float32()
        self.z = stream.read_float32()
        self.smoothing = bool(stream.read_unsigned_char8())

class Edge(SparkDataBlock):

    def __init__(self, id, v1, v2):
        self.id = id
        self.v1 = v1
        self.v2 = v2
        self.is_flipped = False

    def write(self, stream):
        stream.write_unsigned_int32(self.v1)
        stream.write_unsigned_int32(self.v2)
        stream.write_unsigned_char8(int(self.is_flipped))

class Group(SparkDataBlock):

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.color = None
        self.is_visible = True

class EdgeLoop(SparkDataBlock):

    def __init__(self):
        self.edges = []

    def add_edge(self, edge):
        self.edges.append(edge)

    def write(self, stream):
        stream.write_unsigned_int32(len(self.edges))
        for edge in self.edges:
            stream.write_unsigned_int32(edge.is_flipped)
            stream.write_unsigned_int32(edge.id)

        f.write(ctypes.c_uint32(3))     # number of edges in the border edgeloop
        f.write(ctypes.c_uint32(0))     # is_flipped
        f.write(ctypes.c_uint32(2))     # edge index
        f.write(ctypes.c_uint32(0))     # is_flipped
        f.write(ctypes.c_uint32(0))     # edge index
        f.write(ctypes.c_uint32(0))     # is_flipped
        f.write(ctypes.c_uint32(1))     # edge index

class Face(SparkDataBlock):

    def __init__(self, id, border_edgeloop):
        self.id = id
        self.scale = (1.0, 1.0)
        self.offset = (0.0, 0.0)
        self.angle = 0.0
        self.border_edgeloop = border_edgeloop
        self.edgeloops = []
        self.mapping_group = -1
        self.material = -1

    def write(self, stream):
        stream.write_float32(self.angle)
        stream.write_float32(self.offset[0])
        stream.write_float32(self.offset[1])
        stream.write_float32(self.scale[0])
        stream.write_float32(self.scale[1])
        stream.write_unsigned_int32(self.mapping_group)
        stream.write_unsigned_int32(self.material)
        stream.write_unsigned_int32(len(self.edgeloops))
        self.border_edgeloop.write(stream)
        for edgeloop in self.edgeloops:
            edgeloop.write(stream)

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

    def write(self, stream):
        pass

class Material(SparkDataBlock):

    def __init__(self):
        self.chunk_id = 4

    def write(self, stream):
        b_repr = b""
        b_repr += ctypes.c_uint32(chunk_id)
        b_repr += ctypes.c_uint32(chunk_length)
        b_repr += ctypes.c_uint32(num_materials)
        b_repr += ctypes.c_uint32(material_filepath_length)
        b_repr += material_filepath.encode("utf-8")
        return b_repr

    def load(self):
        pass