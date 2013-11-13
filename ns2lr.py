#!/usr/bin/python
# Reads NS2 level file.

import os
import sys

from struct import *


class LevelFileReader:

    """Reads NS2 level files"""

    def __init__(self, filename):
        self.__filename = filename
        self.__bytesread = 0
        self.__materials = []
        self.__version = 0

    def __read_unsigned_int32(self, f):
        data = f.read(4)
        self.__bytesread += 4
        return unpack('I', data)[0]

    def __read_float32(self, f):
        data = f.read(4)
        self.__bytesread += 4
        return unpack('f', data)[0]

    def __read_vec2_float32(self, f):
        data = f.read(8)
        self.__bytesread += 8
        return unpack('ff', data)

    def __read_vec3_float32(self, f):
        data = f.read(12)
        self.__bytesread += 12
        return unpack('fff', data)

    def __read_unsigned_char8(self, f):
        data = f.read(1)
        self.__bytesread += 1
        return unpack('B', data)[0]

    def __read_string(self, f, n):
        data = f.read(n)
        self.__bytesread += n
        return data.decode("utf-8")

    def __read_chunk_object(self, f, chunklen):

        chunk_start_bytesread = self.__bytesread

        has_layerdata = bool(self.__read_unsigned_int32(f))
        print(has_layerdata)
        if has_layerdata:
            layer_format = self.__read_unsigned_int32(f)
            num_layerbitvalues = self.__read_unsigned_int32(f)
            for i in range(num_layerbitvalues):
                bitmask = self.__read_unsigned_int32(f)
        entity_groupid = self.__read_unsigned_int32(f)
        entity_classname_len = self.__read_unsigned_int32(f)
        entity_classname = self.__read_string(f, entity_classname_len)
        print(entity_groupid)
        print(entity_classname_len)
        print(entity_classname)
        while ((self.__bytesread - chunk_start_bytesread) < chunklen):
            object_chunkid = self.__read_unsigned_int32(f)
            wtf = self.__read_unsigned_int32(f)
            object_chunklen = self.__read_unsigned_int32(f)
            print("object_chunkid: "+str(object_chunkid))
            print("wtf: "+str(wtf))
            print("object_chunklen: "+str(object_chunklen))
            prop_name_len = self.__read_unsigned_int32(f)
            prop_name = self.__read_string(f,6)
            print("prop_name_len: "+str(prop_name_len))
            print("prop_name: "+str(prop_name))
            exit(0)
            
        chunk_bytes_read = self.__bytesread - chunk_start_bytesread
        chunk_bytes_left = chunklen - chunk_bytes_read
        if chunk_bytes_left != 0:
            print("[[Error: read " + str(chunk_bytes_read) +
                  " bytes, should be " + str(chunklen) + " bytes]]")
            exit(1)

    def __read_chunk_mesh(self, f, chunklen):

        while self.__bytesread < chunklen:

            mesh_chunkid = self.__read_unsigned_int32(f)
            mesh_chunklen = self.__read_unsigned_int32(f)
            chunk_start_bytesread = self.__bytesread

            # chunk_vertices
            if mesh_chunkid == 1:
                num_vertices = self.__read_unsigned_int32(f)
                while self.__bytesread < (chunk_start_bytesread + mesh_chunklen):
                    vec3 = self.__read_vec3_float32(f)
                    smoothing = bool(self.__read_unsigned_char8(f))

            # chunk_edges
            elif mesh_chunkid == 2:
                num_edges = self.__read_unsigned_int32(f)
                while self.__bytesread < (chunk_start_bytesread + mesh_chunklen):
                    vi_1 = self.__read_unsigned_int32(f)
                    vi_2 = self.__read_unsigned_int32(f)
                    is_flipped = bool(self.__read_unsigned_char8(f))

            # chunk_faces
            elif mesh_chunkid == 3:
                num_faces = self.__read_unsigned_int32(f)
                for i in range(num_faces):
                    angle = self.__read_float32(f)
                    offset = self.__read_vec2_float32(f)
                    scale = self.__read_vec2_float32(f)
                    mapping_group_id = self.__read_unsigned_int32(f)
                    materialid = self.__read_unsigned_int32(f)
                    additional_edgeloops = self.__read_unsigned_int32(f)
                    # account for border edgeloop
                    for j in range(1 + additional_edgeloops):
                        num_edges = self.__read_unsigned_int32(f)
                        for k in range(num_edges):
                            is_flipped = bool(self.__read_unsigned_int32(f))
                            edge_index = self.__read_unsigned_int32(f)

            # chunk_materials
            elif mesh_chunkid == 4:
                nummaterials = self.__read_unsigned_int32(f)
                for i in range(nummaterials):
                    num_chars = self.__read_unsigned_int32(f)
                    material = self.__read_string(f, num_chars)
                    self.__materials.append(material)

            # chunk_triangles
            elif mesh_chunkid == 5:
                num_ghost_vertices = self.__read_unsigned_int32(f)
                for i in range(num_ghost_vertices):
                    ghost_vertex = self.__read_vec3_float32(f)
                num_smoothed_normals = self.__read_unsigned_int32(f)
                for i in range(num_smoothed_normals):
                    smoothed_normal = self.__read_vec3_float32(f)
                num_faces = self.__read_unsigned_int32(f)
                num_triangles = self.__read_unsigned_int32(f)
                for i in range(num_faces):
                    num_face_triangles = self.__read_unsigned_int32(f)
                    for j in range(num_face_triangles):
                        vertex_index1 = self.__read_unsigned_int32(f)
                        vertex_index2 = self.__read_unsigned_int32(f)
                        vertex_index3 = self.__read_unsigned_int32(f)
                        smoothed_normal_index1 = self.__read_unsigned_int32(f)
                        smoothed_normal_index2 = self.__read_unsigned_int32(f)
                        smoothed_normal_index3 = self.__read_unsigned_int32(f)

            # chunk_facelayers
            elif mesh_chunkid == 6:
                num_facelayers = self.__read_unsigned_int32(f)
                format = self.__read_unsigned_int32(f)
                if format != 2:
                    print("error: format is not 2")
                    exit(1)
                for i in range(num_facelayers):
                    has_layers = bool(self.__read_unsigned_int32(f))
                    if has_layers:
                        num_layerbitvalues = self.__read_unsigned_int32(f)
                        for j in range(num_layerbitvalues):
                            bitmask = self.__read_unsigned_int32(f)

            # chunk_mappinggroups
            elif mesh_chunkid == 7:
                num_mappinggroups = self.__read_unsigned_int32(f)
                for i in range(num_mappinggroups):
                    mgid = self.__read_unsigned_int32(f)
                    angle = self.__read_float32(f)
                    scale = self.__read_vec2_float32(f)
                    offset = self.__read_vec2_float32(f)
                    normal = self.__read_vec3_float32(f)

            # chunk_geometrygroups
            elif mesh_chunkid == 8:
                num_vertexgroups = self.__read_unsigned_int32(f)
                for i in range(num_vertexgroups):
                    vgid = self.__read_unsigned_int32(f)
                    num_indices = self.__read_unsigned_int32(f)
                    for j in range(num_indices):
                        index = self.__read_unsigned_int32(f)
                num_edgegroups = self.__read_unsigned_int32(f)
                for i in range(num_edgegroups):
                    egid = self.__read_unsigned_int32(f)
                    num_indices = self.__read_unsigned_int32(f)
                    for j in range(num_indices):
                        index = self.__read_unsigned_int32(f)
                num_facegroups = self.__read_unsigned_int32(f)
                for i in range(num_facegroups):
                    fgid = self.__read_unsigned_int32(f)
                    num_indices = self.__read_unsigned_int32(f)
                    for j in range(num_indices):
                        index = self.__read_unsigned_int32(f)

            # skip this chunk
            else:
                print("unknown mesh chunk id: " + str(mesh_chunkid))
                data = f.read(mesh_chunklen)
                self.__bytesread += mesh_chunklen

            chunk_bytes_read = self.__bytesread - chunk_start_bytesread
            chunk_bytes_left = mesh_chunklen - chunk_bytes_read
            if chunk_bytes_left != 0:
                print("[[Error: read " + str(chunk_bytes_read) +
                      " bytes, should be " + str(mesh_chunklen) + " bytes]]")
                exit(1)

    def __read_chunk_layers(self, f, chunklen):
        data = f.read(chunklen)

    def __read_chunk_viewports(self, f, chunklen):
        data = f.read(chunklen)

    def __read_chunk_groups(self, f, chunklen):
        data = f.read(chunklen)

    def __read_chunk_customcolors(self, f, chunklen):
        data = f.read(chunklen)

    def __read_chunk_editorsettings(self, f, chunklen):
        data = f.read(chunklen)

    def read_level(self):
        with open(self.__filename, "rb") as f:

            magicnumber = self.__read_string(f,3)
            if magicnumber != "LVL":
                print("not a level file")
                exit(1)

            self.__version = self.__read_unsigned_char8(f)
            print("Reading level \"" + self.__filename +
                  "\" (version " + str(self.__version) + ")")

            while True:
                
                chunkid = self.__read_unsigned_int32(f)
                chunklen = self.__read_unsigned_int32(f)

                if chunkid == 1:
                    # print("chunk_object")
                    self.__read_chunk_object(f, chunklen)

                elif chunkid == 2:
                    # print("chunk_mesh")
                    self.__read_chunk_mesh(f, chunklen)

                elif chunkid == 3:
                    # print("chunk_layers")
                    self.__read_chunk_layers(f, chunklen)

                elif chunkid == 4:
                    # print("chunk_viewports")
                    self.__read_chunk_viewports(f, chunklen)

                elif chunkid == 5:
                    # print("chunk_groups")
                    self.__read_chunk_groups(f, chunklen)

                elif chunkid == 6:
                    # print("chunk_customcolors")
                    self.__read_chunk_customcolors(f, chunklen)

                elif chunkid == 7:
                    # print("chunk_editorsettings")
                    self.__read_chunk_editorsettings(f, chunklen)

                else:
                    print("unknown chunk id: " + str(chunkid))
                    #data = f.read(chunklen)
                    exit(1)


def main(args):
    if len(args) < 2:
        sys.exit("Usage: %s FILE" % sys.argv[0])
    if not os.path.exists(sys.argv[1]):
        sys.exit("Error: file %s was not found!" % sys.argv[1])
    filename = sys.argv[1]
    reader = LevelFileReader(filename)
    reader.read_level()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
