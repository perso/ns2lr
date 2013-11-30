import pprint
import sys
from elements.Elements import *
from parsers.levelparser import LevelParser


class LevelReader(object):

    """Reads NS2 level files"""

    def __init__(self):
        self.entities = []
        self.groups = []
        self.vertices = []
        self.edges = []
        self.faces = []

    def write_level(self, filename):
        pass

    def read_level(self, filename):
        parser = LevelParser(filename)
        parser.parse()

        entities = parser.get_entities()
        groups = parser.get_groups()
        mesh = parser.get_mesh()

        vertices = mesh["vertices"]
        edges = mesh["edges"]
        faces = mesh["faces"]
        materials = mesh["materials"]
        face_triangles = mesh["triangles"]

        print("Loaded %d entities." % len(entities))
        print("Loaded %d groups." % len(groups))
        print("Loaded %d vertices." % len(vertices))
        print("Loaded %d edges." % len(edges))
        print("Loaded %d faces." % len(faces))
        print("Loaded %d materials." % len(materials))

        for entity in entities:
            e = Entity(entity["classname"])
            e.groupid = entity["groupid"]
            e.layerdata = entity["layerdata"]
            e.properties = entity["properties"]
            self.entities.append(e)

        for group_id, group in groups.items():
            g = Group(group_id, group["name"])
            g.color = group["color"]
            g.is_visible = group["is_visible"]
            self.groups.append(g)

        for vertex in vertices:
            v = Vertex(vertex["point"]["x"], vertex["point"]["y"], vertex["point"]["y"])
            v.has_smoothing = vertex["has_smoothing"]
            self.vertices.append(v)

        for edge in edges:
            e = Edge(edge["vi_1"], edge["vi_2"])
            e.is_flipped = edge["is_flipped"]
            self.edges.append(e)

        for i, face in enumerate(faces):
            edgeloop = face["border_edgeloop"]
            border_el = EdgeLoop()
            for edge in edgeloop:
                border_el.add_edge(edge["edge_index"], edge["is_flipped"])
            f = Face(border_el)
            f.angle = face["angle"]
            f.offset = face["offset"]
            f.scale = face["scale"]
            f.mapping_group_id = face["mapping_group_id"]
            f.materialid = face["materialid"]

        self.materials = materials

        pprint.pprint(faces[0])
        pprint.pprint(face_triangles[0])
        pprint.pprint(edges[623])
