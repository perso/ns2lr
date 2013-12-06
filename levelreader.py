#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import c_ubyte
import pprint
import sys
import ctypes
import io
from elements.Elements import *
from parsers.binarywriter import BinaryWriter
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

    def write_viewport(self, f):

        with io.open("chunkviewport.bin", "rb") as fh:
            viewport_data = fh.read()
            f.write(viewport_data)

    def write_triangles(self, f):
        f.write(ctypes.c_uint32(5))     # chunk_id (triangles)
        f.write(ctypes.c_uint32(44))    # chunk_length
        f.write(ctypes.c_uint32(0))     # number of ghost vertices
        f.write(ctypes.c_uint32(0))     # number of smoothed normals
        f.write(ctypes.c_uint32(1))     # number of faces
        f.write(ctypes.c_uint32(1))     # number of triangles (total)
        f.write(ctypes.c_uint32(1))     # number of triangles (this face)
        f.write(ctypes.c_uint32(2))     # vertex indices
        f.write(ctypes.c_uint32(1))
        f.write(ctypes.c_uint32(0))
        f.write(ctypes.c_uint32(0))     # smoothed normals
        f.write(ctypes.c_uint32(0))
        f.write(ctypes.c_uint32(0))

    def write_geometrygroups(self, f):
        f.write(ctypes.c_uint32(8))     # chunk_id (geometry groups)
        f.write(ctypes.c_uint32(12))    # chunk_length
        f.write(ctypes.c_uint32(0))
        f.write(ctypes.c_uint32(0))
        f.write(ctypes.c_uint32(0))

    def write_mappinggroups(self, f):
        f.write(ctypes.c_uint32(7))     # chunk_id (mapping groups)
        f.write(ctypes.c_uint32(4))     # chunk_length
        f.write(ctypes.c_uint32(0))     # num mapping groups

    def write_facelayers(self, f):
        f.write(ctypes.c_uint32(6))     # chunk_id (face layers)
        f.write(ctypes.c_uint32(12))    # chunk_length
        f.write(ctypes.c_uint32(1))     # num_facelayers
        f.write(ctypes.c_uint32(2))     # format
        f.write(ctypes.c_uint32(0))     # has_layers

    def write_faces(self, stream, faces):
        chunk_id = 3
        num_faces = len(faces)
        chunk_length = 64
        stream.write_unsigned_int32(chunk_id)
        stream.write_unsigned_int32(chunk_length)
        stream.write_unsigned_int32(num_faces)
        for face in faces:
            face.write(stream)

    def write_edges(self, stream, edges):
        chunk_id = 2
        num_edges = len(edges)
        chunk_length = 4 + (num_edges * 9)
        stream.write_unsigned_int32(chunk_id)
        stream.write_unsigned_int32(chunk_length)
        stream.write_unsigned_int32(num_edges)
        for edge in edges:
            edge.write(stream)

    def write_vertices(self, stream, vertices):
        chunk_id = 1
        num_vertices = len(vertices)
        chunk_length = 4 + (num_vertices * 13)
        stream.write_unsigned_int32(chunk_id)
        stream.write_unsigned_int32(chunk_length)
        stream.write_unsigned_int32(num_vertices)
        for vertex in vertices:
            vertex.write(stream)

    def write_materials(self, stream):

        chunk_id = 4
        num_materials = 1
        material_filepath = "materials/dev/dev_floor_grid.material"
        material_filepath_length = len(material_filepath)
        chunk_length = 8 + material_filepath_length

        stream.write_unsigned_int32(chunk_id)
        stream.write_unsigned_int32(chunk_length)
        stream.write_unsigned_int32(num_materials)
        stream.write_unsigned_int32(material_filepath_length)
        stream.write_string(material_filepath)

    def write_header(self, stream):
        stream.write_string("LVL")
        stream.write_unsigned_char8(10)

    def write_chunk_mesh(self, stream):

        stream.write_unsigned_int32(2)   # chunk_id
        stream.write_unsigned_int32(319) # chunk_length = 43 + 31 + 64 + 45 + 44 + 12 + 4 + 12 + 8*8 = 319

        self.write_materials(stream)

        v1 = Vertex(2.0, 3.0, 5.0)
        v2 = Vertex(1.5, -2.5, 2.0)
        v3 = Vertex(6.0, 2.0, 1.0)
        self.write_vertices(stream, [v1, v2, v3])

        e1 = Edge(v1, v2)
        e2 = Edge(v2, v3)
        e3 = Edge(v3, v1)
        self.write_edges(stream, [e1, e2, e3])

        edgeloop = EdgeLoop()
        edgeloop.add_edge(e1)
        edgeloop.add_edge(e2)
        edgeloop.add_edge(e3)
        self.write_faces(stream, [edgeloop])


        self.write_facelayers(stream)
        self.write_mappinggroups(stream)
        self.write_geometrygroups(stream)
        self.write_triangles(stream)

    def write_editorsettings(self, f):

        with io.open("chunkeditorsettings.bin", "rb") as fh:
            editor_settings_data = fh.read()
            f.write(editor_settings_data)

    def write_level(self, filename):
        #with io.open(filename, "wb") as f:
        #    self.write_header(f)
        #    self.write_chunk_mesh(f)
        #    self.write_viewport(f)
        #    self.write_editorsettings(f)
        stream = BinaryWriter(filename)
        self.write_header(stream)
        self.write_chunk_mesh(stream)
        #self.write_viewport(stream)
        #self.write_editorsettings(stream)

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

        #print("Loaded %d entities." % len(entities))
        #print("Loaded %d groups." % len(groups))
        #print("Loaded %d vertices." % len(vertices))
        #print("Loaded %d edges." % len(edges))
        #print("Loaded %d faces." % len(faces))
        #print("Loaded %d materials." % len(materials))
        #print("Loaded triangles for %d faces." % len(face_triangles))
        #print("Loaded %d customcolors." % len(customcolors))
        #print("Loaded %d layers." % len(layers))
        #print("Loaded %d viewport." % len(viewport))
        #print("Loaded %d editorsettings." % len(editorsettings))
        #print("Loaded %d face_layers." % len(face_layers))
        #print("Loaded %d mapping_groups." % len(mapping_groups))
        #print("Loaded %d geometry_groups." % len(geometry_groups))

        #pprint.pprint(materials)
        #pprint.pprint(faces)
        #pprint.pprint(face_triangles)

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

