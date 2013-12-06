import ctypes
from struct import pack, calcsize


class Level(object):

    def __init__(self):
        pass

    def write(self):
        pass

class ChunkHeader(object):

    def __init__(self, version):
        self.version = version

    def get_length(self):
        pass

    def dump(self):
        return "LVL".encode("utf-8") + pack("B", self.version)

class ChunkMesh(object):

    def __init__(self, vertices=[], edges=[], faces=[]):
        self.id = 2
        self.chunk_vertices = ChunkVertices(vertices)
        self.chunk_edges = ChunkEdges(edges)
        self.chunk_faces = ChunkFaces(faces)

    def get_length(self):
        length = 4
        length += self.chunk_vertices.get_length()

    def dump(self):
        data = pack("II", self.id, self.get_length())
        data += self.chunk_vertices.dump()
        return data

class ChunkGeometrygroups(object):

    def __init__(self):
        pass

    def get_length(self):
        pass

    def dump(self):
        pass

class ChunkMappinggroups(object):

    def __init__(self):
        pass

    def get_length(self):
        pass

    def dump(self):
        pass

class ChunkFacelayers(object):

    def __init__(self):
        pass

    def get_length(self):
        pass

    def dump(self):
        pass

class ChunkFaces(object):

    def __init__(self, faces):
        self.id = 3
        self.faces = faces

    def get_length(self):
        pass

    def dump(self):
        pass

class ChunkEdges(object):

    def __init__(self, edges):
        self.id = 2
        self.edges = edges

    def get_length(self):
        pass

    def dump(self):
        pass

class ChunkVertices(object):

    def __init__(self, vertices):
        self.id = 1
        self.vertices = vertices
        self.format = "III"

    def get_length(self):
        length = calcsize(self.format) - 8
        for vertex in self.vertices:
            length += vertex.get_length()
        return length

    def dump(self):
        chunk_length = self.get_length()
        bytes = pack(self.format, self.id, chunk_length, len(self.vertices))
        for vertex in self.vertices:
            bytes += vertex.dump()
        return bytes

class ChunkTriangles(object):

    def __init__(self):
        self.id = 5
        self.triangles = []
        self.ghostvertices = []
        self.smoothednormals = []

    def get_length(self):
        pass

    def dump(self):
        chunk_length = self.get_length()
        bytes = pack("II", self.id, chunk_length)
        bytes += len(self.ghostvertices)
        for vertex in self.ghostvertices:
            bytes += vertex.dump()
        bytes += len(self.smoothednormals)
        for vector in self.smoothednormals:
            bytes += vector.dump()
        bytes += len(self.triangles)
        for triangle in self.triangles:
            bytes += triangle.dump()
        return bytes

class ChunkMaterials(object):

    def __init__(self):
        self.chunk_id = 4
        self.materials = []

    def dump(self):
        data = pack("III", self.chunk_id, self.get_length(), len(self.materials))
        for material in self.materials:
            data += material.dump()
        return data

    def load(self):
        pass

class Entity(object):

    def __init__(self, classname):
        self.classname = classname
        self.groupid = -1
        self.layerdata = {}
        self.properties = {}

class Vector(object):

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.format = "fff"

    def get_length(self):
        pass

    def dump(self):
        return pack(self.format, self.x, self.y, self.z)

class Vertex(Vector):

    def __init__(self, id, x=0.0, y=0.0, z=0.0, smoothing=False):
        self.id = id
        super(Vertex, self).__init__(x, y, z)
        self.smoothing = smoothing
        self.format = "fffB"

    def get_length(self):
        return calcsize(self.format)

    def dump(self):
        return pack(self.format, self.x, self.y, self.z, self.smoothing)

class Edge(object):

    def __init__(self, id, v1, v2):
        self.id = id
        self.v1 = v1
        self.v2 = v2
        self.is_flipped = False
        self.format = "IIB"

    def get_length(self):
        return calcsize(self.format)

    def dump(self):
        return pack(self.format, self.v1.id, self.v2.id, self.is_flipped)

class Group(object):

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.color = None
        self.is_visible = True

    def get_length(self):
        pass

    def dump(self):
        pass

class EdgeLoop(object):

    def __init__(self, *edges):
        self.edges = list(edges)

    def dump(self):
        data = pack("I", len(self.edges))
        for edge in self.edges:
            data += edge.dump()
        return data

class Face(object):

    def __init__(self, id, border_edgeloop):
        self.id = id
        self.scale = (1.0, 1.0)
        self.offset = (0.0, 0.0)
        self.angle = 0.0
        self.border_edgeloop = border_edgeloop
        self.edgeloops = []
        self.mapping_group = -1
        self.material = -1

    def get_length(self):
        pass

    def dump(self):
        data = pack("fffffIII", self.angle, self.offset[0], self.offset[1], self.scale[0], self.scale[1],
                                self.mapping_group, self.material, len(self.edgeloops))
        data += self.border_edgeloop.dump()
        for edgeloop in self.edgeloops:
            data += edgeloop.dump()
        return data

class Triangle(object):

    def __init__(self, vi_1, vi_2, vi_3, sni_1=0, sni_2=0, sni_3=0):
        self.vi_1 = vi_1
        self.vi_2 = vi_2
        self.vi_3 = vi_3
        self.sni_1 = sni_1
        self.sni_2 = sni_2
        self.sni_3 = sni_3
        self.format = "IIIIII"

    def set_smoothed_normals(self, sni_1, sni_2, sni_3):
        self.sni_1 = sni_1
        self.sni_2 = sni_2
        self.sni_3 = sni_3

    def get_length(self):
        pass

    def dump(self):
        data = pack(self.format, self.vi_1, self.vi_2, self.vi_3, self.sni_1, self.sni_2, self.sni_3)
        return data
