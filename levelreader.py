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
        self.materials = []
        self.vertices = []
        self.edges = []
        self.faces = []
        self.triangles = []
        self.facelayers = []

    def write_viewport(self, stream):
        with io.open("chunkviewport.bin", "rb") as fh:
            viewport_data = fh.read()
            stream.write(viewport_data)

    def write_editorsettings(self, stream):
        with io.open("chunkeditorsettings.bin", "rb") as fh:
            editor_settings_data = fh.read()
            stream.write(editor_settings_data)

    def write_header(self, stream, version):
        chunk = ChunkHeader(version)
        stream.write(chunk.dump())

    def write_mesh(self, stream):
        materials = (
            "materials/dev/dev_floor_grid.material",
            "materials/dev/dev_1024x1024.material",
        )
        vertices = [
            Vertex(0, 0.0, 0.0, 0.0),
            Vertex(1, 0.0, 0.0, 5.0),
            Vertex(2, 5.0, 0.0, 5.0),
            Vertex(3, 5.0, 0.0, 0.0),
        ]
        edges = [
            Edge(0, vertices[0], vertices[1]),
            Edge(1, vertices[1], vertices[2]),
            Edge(2, vertices[2], vertices[0]),
            Edge(3, vertices[2], vertices[3]),
            Edge(4, vertices[3], vertices[0]),
        ]
        faces = [
            Face(0, EdgeLoop([
                {"edge": edges[0], "is_flipped": False},
                {"edge": edges[1], "is_flipped": False},
                {"edge": edges[2], "is_flipped": False}]), 0),
            Face(1, EdgeLoop([
                {"edge": edges[2], "is_flipped": True},
                {"edge": edges[3], "is_flipped": False},
                {"edge": edges[4], "is_flipped": False}]), 1),
        ]
        triangles = {
            "total": 2,
            "faces": [
                [
                    Triangle(vertices[0], vertices[1], vertices[2]),
                ],
                [
                    Triangle(vertices[1], vertices[2], vertices[3]),
                ]
            ]
        }
        facelayers = [
            {"has_layers": 0},
            {"has_layers": 0},
        ]

        #chunk = ChunkMesh(materials=materials, vertices=vertices, edges=edges, faces=faces, triangles=triangles, facelayers=facelayers)
        chunk = ChunkMesh(materials=self.materials, vertices=self.vertices, edges=self.edges, faces=self.faces,
                          triangles=self.triangles, facelayers=self.facelayers)
        stream.write(chunk.dump())

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

        pprint.pprint(mesh)

        self.materials = mesh["materials"]
        for i, vertex in enumerate(mesh["vertices"]):
            self.vertices.append(Vertex(i, vertex["x"], vertex["y"], vertex["z"]))
        for i, edge in enumerate(mesh["edges"]):
            self.edges.append(Edge(i, self.vertices[edge["vi_1"]], self.vertices[edge["vi_2"]]))
        #for i, face in enumerate(mesh["faces"]):
        #    border = []
        #    for edge in face["border_edgeloop"]:
        #        border.append({"edge": self.edges[edge["edge_index"]], "is_flipped": edge["is_flipped"]})
        #    self.faces.append(Face(i, EdgeLoop(border), face["materialid"]))
