import ctypes
from struct import pack, calcsize


class Level(object):

    def __init__(self):
        pass

    def write(self):
        pass

class ChunkHeader(object):

    def __init__(self, version):
        self.magicnumber = "LVL"
        self.version = version

    def get_length(self):
        return 4

    def dump(self):
        return self.magicnumber.encode("utf-8") + pack("B", self.version)

class ChunkMesh(object):

    def __init__(self, vertices=(), edges=(), faces=(), materials=(), facelayers=(), mappinggroups=(), geometrygroups=(), triangles={}):
        self.id = 2
        self.chunks = {
            "materials": ChunkMaterials(materials),
            "vertices": ChunkVertices(vertices),
            "edges": ChunkEdges(edges),
            "faces": ChunkFaces(faces),
            "facelayers": ChunkFacelayers(facelayers),
            "mappinggroups": ChunkMappinggroups(mappinggroups),
            "geometrygroups": ChunkGeometrygroups(geometrygroups),
            "triangles": ChunkTriangles(triangles)
        }
        self.format = "II"

    def get_length(self):
        length = 0
        for chunk_name, chunk in list(self.chunks.items()):
            if not chunk.empty():
                length += chunk.get_length()
        if length > 0:
            length += calcsize(self.format)
        return length

    def dump(self):
        data = b""
        if self.get_length() > 0:
            chunk_length = self.get_length() - 8
            data += pack(self.format, self.id, chunk_length)
            for chunk_name, chunk in list(self.chunks.items()):
                if not chunk.empty():
                    data += chunk.dump()
        return data

class ChunkGeometrygroups(object):

    def __init__(self, geometrygroups):
        self.geometrygroups = geometrygroups

    def empty(self):
        return not self.geometrygroups

    def get_length(self):
        pass

    def dump(self):
        pass

class ChunkMappinggroups(object):

    def __init__(self, mappinggroups):
        self.mappinggroups = mappinggroups

    def empty(self):
        return not self.mappinggroups

    def get_length(self):
        pass

    def dump(self):
        pass

class ChunkFacelayers(object):

    def __init__(self, facelayers):
        self.facelayers = facelayers

    def empty(self):
        return not self.facelayers

    def get_length(self):
        pass

    def dump(self):
        pass

class ChunkFaces(object):

    def __init__(self, faces):
        self.id = 3
        self.faces = faces
        self.format = "III"

    def empty(self):
        return not self.faces

    def get_length(self):
        length = calcsize(self.format)
        for face in self.faces:
            length += face.get_length()
        return length

    def dump(self):
        chunk_length = self.get_length() - 8
        bytes = pack(self.format, self.id, chunk_length, len(self.faces))
        for face in self.faces:
            bytes += face.dump()
        return bytes

class ChunkEdges(object):

    def __init__(self, edges):
        self.id = 2
        self.edges = edges
        self.format = "III"

    def empty(self):
        return not self.edges

    def get_length(self):
        length = calcsize(self.format)
        for edge in self.edges:
            length += edge.get_length()
        return length

    def dump(self):
        chunk_length = self.get_length() - 8
        bytes = pack(self.format, self.id, chunk_length, len(self.edges))
        for edge in self.edges:
            bytes += edge.dump()
        return bytes

class ChunkVertices(object):

    def __init__(self, vertices):
        self.id = 1
        self.vertices = vertices
        self.format = "III"

    def empty(self):
        return not self.vertices

    def get_length(self):
        length = calcsize(self.format)
        for vertex in self.vertices:
            length += vertex.get_length()
        return length

    def dump(self):
        chunk_length = self.get_length() - 8
        bytes = pack(self.format, self.id, chunk_length, len(self.vertices))
        for vertex in self.vertices:
            bytes += vertex.dump()
        return bytes

class ChunkTriangles(object):

    def __init__(self, triangles):
        self.id = 5
        self.ghostvertices = triangles["ghostvertices"]
        self.smoothednormals = triangles["smoothednormals"]
        self.triangles = triangles["triangles"]

    def empty(self):
        return not (self.ghostvertices or self.smoothednormals or self.triangles)

    def get_length(self):
        return 20

    def dump(self):
        chunk_length = self.get_length() - 8
        bytes = pack("II", self.id, chunk_length)
        bytes += pack("I", len(self.ghostvertices))
        for vertex in self.ghostvertices:
            bytes += vertex.dump()
        bytes += pack("I", len(self.smoothednormals))
        for vector in self.smoothednormals:
            bytes += vector.dump()
        bytes += pack("I", len(self.triangles))
        for triangle in self.triangles:
            bytes += triangle.dump()
        return bytes

class ChunkMaterials(object):

    def __init__(self, materials):
        self.id = 4
        self.materials = materials
        self.format = "III"

    def empty(self):
        return not self.materials

    def get_length(self):
        length = calcsize(self.format)
        for material in self.materials:
            length += 4 + len(material)
        return length

    def dump(self):
        chunk_length = self.get_length() - 8
        data = b""
        data += pack(self.format, self.id, chunk_length, len(self.materials))
        for material in self.materials:
            data += pack("I", len(material))
            encoded = material.encode("utf-8")
            data += encoded
        return data

class Vector(object):

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.format = "fff"

    def get_length(self):
        return calcsize(self.format)

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
        return pack(self.format, self.x, self.y, self.z, int(self.smoothing))

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
        return pack(self.format, self.v1.id, self.v2.id, int(self.is_flipped))

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
        self.format = "I"

    def get_length(self):
        length = calcsize(self.format)
        for edge in self.edges:
            length += calcsize("II")
        return length

    def dump(self):
        data = pack(self.format, len(self.edges))
        for edge in self.edges:
            data += pack("II", int(edge.is_flipped), edge.id)
        return data

class Face(object):

    def __init__(self, id, border_edgeloop):
        self.id = id
        self.scale = (1.0, 1.0)
        self.offset = (0.0, 0.0)
        self.angle = 0.0
        self.border_edgeloop = border_edgeloop
        self.edgeloops = []
        self.mapping_group = 4294967295
        self.material = 4294967295
        self.format = "fffffIII"

    def get_length(self):
        length = calcsize(self.format)
        length += self.border_edgeloop.get_length()
        for edgeloop in self.edgeloops:
            length += edgeloop.get_length()
        return length

    def dump(self):
        data = pack(
            self.format,
            self.angle,
            self.offset[0],
            self.offset[1],
            self.scale[0],
            self.scale[1],
            self.mapping_group,
            self.material,
            len(self.edgeloops)
        )
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
        return calcsize(self.format)

    def dump(self):
        data = pack(self.format, self.vi_1, self.vi_2, self.vi_3, self.sni_1, self.sni_2, self.sni_3)
        return data
