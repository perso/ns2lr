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

    def write_viewport(self, stream):
        with io.open("chunkviewport.bin", "rb") as fh:
            viewport_data = fh.read()
            stream.write(viewport_data)

    def write_editorsettings(self, stream):
        with io.open("chunkeditorsettings.bin", "rb") as fh:
            editor_settings_data = fh.read()
            stream.write(editor_settings_data)

    def write_triangles(self, stream, ghostvertices, smoothednormals, triangles):
        chunk = ChunkTriangles(ghostvertices, smoothednormals, triangles)
        stream.write(chunk)

    def write_geometrygroups(self, stream, geometrygroups):
        chunk = ChunkGeometrygroups(geometrygroups)
        stream.write(chunk.dump())

    def write_mappinggroups(self, stream, mappinggroups):
        chunk = ChunkMappinggroups(mappinggroups)
        stream.write(chunk.dump())

    def write_facelayers(self, stream, facelayers):
        chunk = ChunkFacelayers(facelayers)
        stream.write(chunk.dump())

    def write_faces(self, stream, faces):
        chunk = ChunkFaces(faces)
        stream.write(chunk.dump())

    def write_edges(self, stream, edges):
        chunk = ChunkEdges(edges)
        stream.write(chunk.dump())

    def write_vertices(self, stream, vertices):
        chunk = ChunkVertices(vertices)
        stream.write(chunk.dump())

    def write_materials(self, stream, materials):
        chunk = ChunkMaterials(materials)
        stream.write(chunk.dump())

    def write_header(self, stream, version):
        chunk = ChunkHeader(version)
        stream.write(chunk.dump())

    def write_mesh(self, stream):
        materials = (
            "materials/dev/dev_floor_grid.material",
            "materials/descent/descent_wall_01_a.material",
            "materials/descent/descent_floor_05.material",
        )
        vertices = (
            Vertex(0, 5.0, 0.0, 0.0),
            Vertex(2, 0.0, 5.0, 0.0),
            Vertex(3, 5.0, 0.0, 5.0),
            Vertex(4, 0.0, 5.0, 5.0),
        )
        edges = (
            Edge(0, vertices[0], vertices[1]),
            Edge(1, vertices[1], vertices[2]),
            Edge(2, vertices[2], vertices[0]),
            Edge(3, vertices[2], vertices[3]),
        )
        faces = (
            Face(0, EdgeLoop(edges[0], edges[1], edges[2])),
            Face(1, EdgeLoop(edges[1], edges[2], edges[3])),
        )
        facelayers = (

        )
        mappinggroups = (

        )
        geometrygroups = (

        )
        triangles = {
            "ghostvertices": (

            ),
            "smoothednormals": (

            ),
            "triangles": (

            )
        }

        chunk = ChunkMesh(materials=materials, vertices=vertices, edges=edges, faces=faces, facelayers=facelayers,
                          mappinggroups=mappinggroups, geometrygroups=geometrygroups, triangles=triangles)
        stream.write(chunk.dump())

        #self.write_facelayers(stream, facelayers)
        #self.write_mappinggroups(mappinggroups)
        #self.write_geometrygroups(geometrygroups)
        #self.write_triangles(stream, ghostvertices, smoothednormals, triangles)

    def write_level(self, filename):
        stream = io.open(filename, "wb")
        self.write_header(stream, 10)
        self.write_mesh(stream)
        self.write_viewport(stream)
        self.write_editorsettings(stream)

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
