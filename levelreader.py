#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import c_ubyte
import pprint
import sys
import ctypes
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

        self.viewport = ""
        self.editorsettings = ""

    def write_level(self, filename):
        with open(filename, "wb") as f:
            f.write("LVL".encode("utf-8"))  # magic number
            f.write(ctypes.c_ubyte(10))     # version

            f.write(ctypes.c_uint32(2))     # chunk_id (mesh)
            f.write(ctypes.c_uint32(242))    # chunk_length = 43 + 31 + 64 + 20 + 44 + 5*8 = 242

            # VERTICES

            f.write(ctypes.c_uint32(1))     # chunk_id (vertices)
            f.write(ctypes.c_uint32(43))    # chunk_length

            f.write(ctypes.c_uint32(3))     # number of vertices

            f.write(ctypes.c_float(0.0))    # vertex 1 (index=0)
            f.write(ctypes.c_float(0.0))
            f.write(ctypes.c_float(0.0))
            f.write(ctypes.c_ubyte(0))

            f.write(ctypes.c_float(0.0))    # vertex 2 (index=1)
            f.write(ctypes.c_float(0.0))
            f.write(ctypes.c_float(3.0))
            f.write(ctypes.c_ubyte(0))

            f.write(ctypes.c_float(0.0))    # vertex 3 (index=2)
            f.write(ctypes.c_float(3.0))
            f.write(ctypes.c_float(0.0))
            f.write(ctypes.c_ubyte(0))

            # EDGES

            f.write(ctypes.c_uint32(2))     # chunk_id (edges)
            f.write(ctypes.c_uint32(31))    # chunk_length

            f.write(ctypes.c_uint32(3))     # number of edges

            f.write(ctypes.c_uint32(0))      # v1 of edge 1
            f.write(ctypes.c_uint32(1))      # v2 of edge 1
            f.write(ctypes.c_ubyte(0))       # is_flipped

            f.write(ctypes.c_uint32(1))      # v1 of edge 2
            f.write(ctypes.c_uint32(2))      # v2 of edge 2
            f.write(ctypes.c_ubyte(0))       # is_flipped

            f.write(ctypes.c_uint32(2))      # v1 of edge 3
            f.write(ctypes.c_uint32(0))      # v2 of edge 3
            f.write(ctypes.c_ubyte(0))       # is_flipped

            # FACES

            f.write(ctypes.c_uint32(3))     # chunk_id (faces)
            f.write(ctypes.c_uint32(64))    # chunk_length

            f.write(ctypes.c_uint32(1))     # number of faces

            f.write(ctypes.c_float(0))     # angle
            f.write(ctypes.c_float(0))     # offset 1
            f.write(ctypes.c_float(0))     # offset 2
            f.write(ctypes.c_float(1.0))     # scale 1
            f.write(ctypes.c_float(1.0))     # scale 2
            f.write(ctypes.c_uint32(4294967295))       # mapping_group_id
            f.write(ctypes.c_uint32(0))       # material_id
            f.write(ctypes.c_uint32(0))       # number of additional edgeloops

            # the border edgeloop
            f.write(ctypes.c_uint32(3))     # number of edges in the border edgeloop

            f.write(ctypes.c_uint32(0))     # is_flipped
            f.write(ctypes.c_uint32(0))     # edge index

            f.write(ctypes.c_uint32(0))     # is_flipped
            f.write(ctypes.c_uint32(1))     # edge index

            f.write(ctypes.c_uint32(0))     # is_flipped
            f.write(ctypes.c_uint32(2))     # edge index

            # MATERIALS

            f.write(ctypes.c_uint32(4))     # chunk_id (materials)
            f.write(ctypes.c_uint32(20))    # chunk_length

            f.write(ctypes.c_uint32(1))    # number of materials
            f.write(ctypes.c_uint32(12))      # number of characters in material filename (including path)
            f.write(u"abc.material".encode("utf-8")) # material filename (including path)

            # TRIANGLES

            f.write(ctypes.c_uint32(5))     # chunk_id (triangles)
            f.write(ctypes.c_uint32(44))    # chunk_length

            f.write(ctypes.c_uint32(0))     # number of ghost vertices
            f.write(ctypes.c_uint32(0))     # number of smoothed normals
            f.write(ctypes.c_uint32(1))     # number of faces
            f.write(ctypes.c_uint32(1))     # number of triangles (total)
            f.write(ctypes.c_uint32(1))     # number of triangles (this face)

            f.write(ctypes.c_uint32(0))     # vertex indices
            f.write(ctypes.c_uint32(1))
            f.write(ctypes.c_uint32(2))

            f.write(ctypes.c_uint32(0))     # smoothed normals
            f.write(ctypes.c_uint32(0))
            f.write(ctypes.c_uint32(0))

            #utf8_encoded_xml_data = (self.viewport[0]+"\n").encode("utf-8")
            #f.write(ctypes.c_uint32(4))     # chunk_id (viewport)
            #f.write(ctypes.c_uint32(len(utf8_encoded_xml_data)+4))      # chunk_length
            #f.write(ctypes.c_uint32(len(utf8_encoded_xml_data)/2))    # length of utf-8 encoded xml in unicode characters
            #f.write(utf8_encoded_xml_data)
            #print("\ntest: %d" % len(utf8_encoded_xml_data))

            #f.write(ctypes.c_uint32(7))
            #f.write(ctypes.c_uint32(len(self.editorsettings)))    # chunk_length
            #f.write(self.editorsettings)

    def read_level(self, filename):
        parser = LevelParser(filename)
        parser.parse()

        entities = parser.get_entities()
        groups = parser.get_groups()
        mesh = parser.get_mesh()
        customcolors = parser.get_customcolors()
        layers = parser.get_layers()
        viewport = parser.get_viewport()
        editorsettings = parser.get_editorsettings()

        vertices = mesh["vertices"]
        edges = mesh["edges"]
        faces = mesh["faces"]
        materials = mesh["materials"]
        face_triangles = mesh["triangles"]
        ghost_vertices = mesh["ghost_vertices"]
        smoothed_normals = mesh["smoothed_normals"]
        face_layers = mesh["face_layers"]
        mapping_groups = mesh["mapping_groups"]
        geometry_groups = mesh["geometry_groups"]

        print("Loaded %d entities." % len(entities))
        print("Loaded %d groups." % len(groups))
        print("Loaded %d vertices." % len(vertices))
        print("Loaded %d edges." % len(edges))
        print("Loaded %d faces." % len(faces))
        print("Loaded %d materials." % len(materials))
        print("Loaded triangles for %d faces." % len(face_triangles))
        print("Loaded %d customcolors." % len(customcolors))
        print("Loaded %d layers." % len(layers))
        print("Loaded %d viewport." % len(viewport))
        print("Loaded %d editorsettings." % len(editorsettings))
        print("Loaded %d face_layers." % len(face_layers))
        print("Loaded %d mapping_groups." % len(mapping_groups))
        print("Loaded %d geometry_groups." % len(geometry_groups))


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
            e = Edge(self.vertices[edge["vi_1"]], self.vertices[edge["vi_2"]])
            e.is_flipped = edge["is_flipped"]
            self.edges.append(e)

        for i, face in enumerate(faces):
            border_edgeloop = EdgeLoop()
            for edge in face["border_edgeloop"]:
                border_edgeloop.add_edge(self.edges[edge["edge_index"]])
            f = Face(border_edgeloop)
            f.angle = face["angle"]
            f.offset = face["offset"]
            f.scale = face["scale"]
            f.mapping_group_id = face["mapping_group_id"]
            f.material = materials[face["materialid"]]

        self.materials = materials

        #pprint.pprint(vertices)
        #pprint.pprint(edges)
        #pprint.pprint(faces)
        #pprint.pprint(materials)
        #print(editorsettings)
        if len(ghost_vertices) > 0:
            pprint.pprint(ghost_vertices[0])

        if len(smoothed_normals) > 0:
            pprint.pprint(smoothed_normals[0])

        if len(face_triangles) > 0:
            pprint.pprint(face_triangles[0])

        self.viewport = viewport
        self.editorsettings = editorsettings

        v1 = Vertex(2.0, 2.0, 2.0)
        v2 = Vertex(2.0, 2.0, 4.0)
        v3 = Vertex(2.0, 4.0, 4.0)
        v4 = Vertex(2.0, 4.0, 2.0)

        el = EdgeLoop()
        el.add_edge(Edge(v1, v2))
        el.add_edge(Edge(v2, v3))
        el.add_edge(Edge(v3, v4))
        el.add_edge(Edge(v4, v1))

        f = Face(el)

