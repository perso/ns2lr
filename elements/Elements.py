import ctypes
import pprint
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

    def __init__(self, vertices=(), edges=(), faces=(), materials=(), facelayers=(), mappinggroups=(),
                       geometrygroups=(), triangles={}, smoothednormals=(), ghostvertices=()):
        self.id = 2
        self.chunks = [
            ChunkMaterials(materials),
            ChunkVertices(vertices),
            ChunkEdges(edges),
            ChunkFaces(faces),
            ChunkFacelayers(facelayers),
            ChunkMappinggroups(mappinggroups),
            ChunkGeometrygroups(geometrygroups),
            ChunkTriangles(ghostvertices, smoothednormals, triangles)
        ]
        self.format = "II"

    def get_length(self):
        length = 0
        for chunk in self.chunks:
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
            for chunk in self.chunks:
                if not chunk.empty():
                    data += chunk.dump()
        return data

class ChunkGeometrygroups(object):

    def __init__(self, geometrygroups):
        self.id = 8
        self.geometrygroups = geometrygroups
        self.format = "IIIII"

    def empty(self):
        return False

    def get_length(self):
        return calcsize(self.format)

    def dump(self):
        chunk_length = self.get_length() - 8
        num_vertexgroups = 0
        num_edgegroups = 0
        num_facegroups = 0
        return pack(self.format, self.id, chunk_length, num_vertexgroups, num_edgegroups, num_facegroups)

class ChunkMappinggroups(object):

    def __init__(self, mappinggroups):
        self.id = 7
        self.mappinggroups = mappinggroups
        self.format = "III"

    def empty(self):
        return False

    def get_length(self):
        return calcsize(self.format)

    def dump(self):
        chunk_length = self.get_length() - 8
        num_mappinggroups = 0
        return pack(self.format, self.id, chunk_length, num_mappinggroups)

class ChunkFacelayers(object):

    def __init__(self, facelayers):
        self.id = 6
        self.facelayers = facelayers
        self.format = "IIII"

    def empty(self):
        return False

    def get_length(self):
        length = calcsize(self.format)
        for facelayer in self.facelayers:
            length += facelayer.get_length()
        return length

    def dump(self):
        chunk_length = self.get_length() - 8
        num_facelayers = len(self.facelayers)
        format = 2
        data = pack(self.format, self.id, chunk_length, num_facelayers, format)
        for facelayer in self.facelayers:
            data += facelayer.dump()
        return data

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

    def __init__(self, ghostvertices, smoothednormals, triangles):
        self.id = 5
        self.ghostvertices = ghostvertices
        self.smoothednormals = smoothednormals
        self.total = 0
        self.faces = []
        if triangles:
            self.total = triangles["total"]
            self.faces = triangles["faces"]

    def empty(self):
        return not (self.ghostvertices or self.smoothednormals or self.faces)

    def get_length(self):
        length = 6*4
        for vertex in self.ghostvertices:
            length += vertex.get_length()
        for vector in self.smoothednormals:
            length += vector.get_length()
        for face_triangles in self.faces:
            length += 4
            for triangle in face_triangles:
                length += triangle.get_length()
        return length

    def dump(self):
        chunk_length = self.get_length() - 8
        bytes = pack("II", self.id, chunk_length)
        bytes += pack("I", len(self.ghostvertices))
        for vertex in self.ghostvertices:
            bytes += vertex.dump()
        bytes += pack("I", len(self.smoothednormals))
        for vector in self.smoothednormals:
            bytes += vector.dump()
        bytes += pack("II", len(self.faces), self.total)
        for face_triangles in self.faces:
            bytes += pack("I", len(face_triangles))
            for triangle in face_triangles:
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

    def __init__(self, id=0, x=0.0, y=0.0, z=0.0):
        self.id = id
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
        super(Vertex, self).__init__(id, x, y, z)
        self.smoothing = smoothing
        self.format = "fffB"

    def get_length(self):
        return calcsize(self.format)

    def dump(self):
        return pack(self.format, self.x, self.y, self.z, int(self.smoothing))

class Edge(object):

    def __init__(self, id, v1, v2, smooth=False):
        self.id = id
        self.v1 = v1
        self.v2 = v2
        self.smooth = smooth
        self.format = "IIB"

    def get_length(self):
        return calcsize(self.format)

    def dump(self):
        return pack(self.format, self.v1.id, self.v2.id, int(self.smooth))

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

    def __init__(self, edges):
        self.edges = edges
        self.format = "I"

    def get_length(self):
        length = calcsize(self.format)
        for edge in self.edges:
            length += calcsize("II")
        return length

    def dump(self):
        data = pack(self.format, len(self.edges))
        for edge in self.edges:
            data += pack("II", int(edge["is_flipped"]), edge["edge"].id)
        return data

class Face(object):

    def __init__(self, id, border_edgeloop, material, scale=(1.0, 1.0),
                 offset=(0.0, 0.0), angle=0.0, mapping_group=4294967295):
        self.id = id
        self.scale = scale
        self.offset = offset
        self.angle = angle
        self.border_edgeloop = border_edgeloop
        self.edgeloops = []
        self.mapping_group = mapping_group
        self.material = material
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

    def __init__(self, v1, v2, v3, n1=Vector(), n2=Vector(), n3=Vector()):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.format = "IIIIII"

    def get_length(self):
        return calcsize(self.format)

    def dump(self):
        data = pack(self.format, self.v1.id, self.v2.id, self.v3.id, self.n1.id, self.n2.id, self.n3.id)
        return data

class Facelayer(object):

    def __init__(self, bitvalues):
        self.bitvalues = bitvalues
        if len(self.bitvalues) > 0:
            self.has_layers = True
        else:
            self.has_layers = False

    def get_length(self):
        length = 4
        if self.has_layers:
            length += 4
        for bitvalue in self.bitvalues:
            length += 4
        return length

    def dump(self):
        data = pack("I", int(self.has_layers))
        if self.has_layers:
            data += pack("I", len(self.bitvalues))
            for bitvalue in self.bitvalues:
                data += pack("I", bitvalue)
        return data
