import pprint
import sys
from elements.Elements import Entity, Group
from parsers.levelparser import LevelParser


class LevelReader(object):

    """Reads NS2 level files"""

    def __init__(self):
        self.entities = []

    def read_level(self, filename):
        parser = LevelParser(filename)
        parser.parse()

        entities = parser.get_entities()
        print("Loaded %d entities." % len(entities))
        groups = parser.get_groups()
        print("Loaded %d groups." % len(groups))
        mesh = parser.get_mesh()

        vertices = mesh["vertices"]
        edges = mesh["edges"]
        faces = mesh["faces"]
        materials = mesh["materials"]
        triangles = mesh["triangles"]

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

        for i, material in enumerate(materials):
            print("%d: %s" % (i, material))

