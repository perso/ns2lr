#!/usr/bin/python
# Reads NS2 level file.

import os
import sys
import pprint

from struct import *


class ReadError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LevelFileReader:

    """Reads NS2 level files"""

    def __init__(self, filename):
        self.__filename = filename
        self.__level_data = ""
        self.__bytesread = 0
        self.__materials = []
        self.__version = 0
        self.__entity_properties = {}
        self.__skipped_chunks_count = 0

    def __read_bytes(self, n):
        data = self.__level_data[self.__bytesread:self.__bytesread + n]
        if len(data) < n:
            raise ReadError(
                "Error: expected %d bytes, read %d" % (n, len(data)))
        else:
            self.__bytesread += n
            return data

    def __read_unsigned_char8(self):
        data = self.__read_bytes(1)
        return unpack('B', data)[0]

    def __read_unsigned_int32(self):
        data = self.__read_bytes(4)
        return unpack('I', data)[0]

    def __read_signed_int32(self):
        data = self.__read_bytes(4)
        return unpack('i', data)[0]

    def __read_float32(self):
        data = self.__read_bytes(4)
        return unpack('f', data)[0]

    def __read_vec2_float32(self):
        data = self.__read_bytes(8)
        return unpack('ff', data)

    def __read_vec3_float32(self):
        data = self.__read_bytes(12)
        return unpack('fff', data)

    def __read_string(self, n):
        data = self.__read_bytes(n)
        return data.decode("utf-8")

    def __read_chunk(self, chunkid, chunkstart, chunklen):

        if chunkid == 1:
            self.__read_chunk_object(chunkstart, chunklen)
        elif chunkid == 2:
            while self.__bytesread < chunklen:
                mesh_chunkid = self.__read_unsigned_int32()
                mesh_chunklen = self.__read_unsigned_int32()
                mesh_chunkstart = self.__bytesread
                self.__read_chunk_mesh(
                    mesh_chunkid, mesh_chunkstart, mesh_chunklen)
        elif chunkid == 3:
            self.__read_chunk_layers(chunkstart, chunklen)
        elif chunkid == 4:
            self.__read_chunk_viewports(chunkstart, chunklen)
        elif chunkid == 5:
            self.__read_chunk_groups(chunkstart, chunklen)
        elif chunkid == 6:
            self.__read_chunk_customcolors(chunkstart, chunklen)
        elif chunkid == 7:
            self.__read_chunk_editorsettings(chunkstart, chunklen)
        else:
            sys.exit("Error: unknown chunk id: %d" % (chunkid))
            data = self.__read_bytes(chunklen)
        chunk_bytes_read = self.__bytesread - chunkstart
        chunk_bytes_left = chunklen - chunk_bytes_read
        if chunk_bytes_left != 0:
            sys.exit("Error: read %d bytes, should be %d bytes" %
                    (chunk_bytes_read, chunklen))

    def __read_chunk_object(self, chunkstart, chunklen):

        has_layerdata = bool(self.__read_unsigned_int32())
        if has_layerdata:
            layer_format = self.__read_unsigned_int32()
            num_layerbitvalues = self.__read_unsigned_int32()
            for i in range(num_layerbitvalues):
                bitmask = self.__read_unsigned_int32()

        entity_groupid = self.__read_unsigned_int32()
        entity_classname_len = self.__read_unsigned_int32()
        entity_classname = self.__read_string(entity_classname_len)
        property_dict = {}

        if self.__version == 10:
            num_properties = self.__read_unsigned_int32()

        while ((self.__bytesread - chunkstart) < chunklen):

            prop_chunkid = self.__read_unsigned_int32()
            if self.__version == 10 and (prop_chunkid != 2):
                continue
            prop_chunklen = self.__read_unsigned_int32()
            prop_name_len = self.__read_unsigned_int32()
            prop_name = self.__read_string(prop_name_len)
            prop_type = self.__read_unsigned_int32()
            num_components = self.__read_unsigned_int32()
            is_animated = bool(self.__read_unsigned_int32())

            # Type_Float
            if (prop_type in (2, 5, 6, 7, 8, 9)):

                if prop_name not in property_dict:
                    property_dict[prop_name] = []

                components = []

                for i in range(num_components):
                    if i < 4:
                        # Components beyond the fourth are ignored
                        component_value = self.__read_float32()
                        components.append(component_value)

                # Next the components are assigned based on the type of
                # property

                # Type_Real, Type_Percentage, Type_Time, and Type_Distance use
                # only the first component
                if (prop_type in (2, 6, 8, 9)):
                    property_dict[prop_name] = components[0]

                # Type_Angle uses component 1 for roll, component 2 for pitch,
                # and component 3 for yaw
                if (prop_type == 7):

                    if len(components) == 3:
                        property_dict[prop_name].append({"roll": components[0],
                                                         "pitch": components[1],
                                                         "yaw": components[2]})
                    elif len(components) == 2:
                        property_dict[prop_name].append({"roll": components[0],
                                                         "pitch": components[1]})
                    elif len(components) == 1:
                        property_dict[prop_name].append(
                            {"roll": components[0]})
                    else:
                        sys.exit(
                            "Error: Type_Angle requires at least one component.")

                # Type_Color uses component 1 for red, component 2 for green,
                # component 3 for blue, and component 4 for alpha
                # (alpha defaults to 1 if there is no component 4)
                if (prop_type == 5):
                    if len(components) < 4:
                        alpha = 1
                    else:
                        alpha = components[3]
                    property_dict[prop_name].append({"red": components[0],
                                                     "green": components[1],
                                                     "blue": components[2]})

            elif (prop_type in (0, 1, 3, 4, 10)):

                if prop_name not in property_dict:
                    property_dict[prop_name] = None

                # Type_String
                if (prop_type in (0, 4)):
                    wide_string_len = self.__read_unsigned_int32()
                    wide_string_value = self.__read_string(2 * wide_string_len)
                    property_dict[prop_name] = wide_string_value

                # Type_Boolean
                elif (prop_type == 1):
                    boolean_value = bool(self.__read_unsigned_int32())
                    property_dict[prop_name] = boolean_value

                # Type_Integer
                elif (prop_type == 3):
                    integer_value = self.__read_signed_int32()
                    property_dict[prop_name] = integer_value

                # Type_Choice
                elif (prop_type == 10):
                    choice_value = self.__read_signed_int32()
                    property_dict[prop_name] = choice_value

            else:
                sys.exit("Error: invalid property type: %d" % prop_type)

        if property_dict:
            if entity_classname not in self.__entity_properties:
                self.__entity_properties[entity_classname] = []
            self.__entity_properties[entity_classname].append(property_dict)

    def __read_chunk_mesh(self, chunkid, chunkstart, chunklen):

        # Chunk_Vertices
        if chunkid == 1:
            num_vertices = self.__read_unsigned_int32()
            while self.__bytesread < (chunkstart + chunklen):
                vec3 = self.__read_vec3_float32()
                smoothing = bool(self.__read_unsigned_char8())

        # Chunk_Edges
        elif chunkid == 2:
            num_edges = self.__read_unsigned_int32()
            while self.__bytesread < (chunkstart + chunklen):
                vi_1 = self.__read_unsigned_int32()
                vi_2 = self.__read_unsigned_int32()
                is_flipped = bool(self.__read_unsigned_char8())

        # Chunk_Faces
        elif chunkid == 3:
            num_faces = self.__read_unsigned_int32()
            for i in range(num_faces):
                angle = self.__read_float32()
                offset = self.__read_vec2_float32()
                scale = self.__read_vec2_float32()
                mapping_group_id = self.__read_unsigned_int32()
                materialid = self.__read_unsigned_int32()
                additional_edgeloops = self.__read_unsigned_int32()
                # account for border edgeloop
                for j in range(1 + additional_edgeloops):
                    num_edges = self.__read_unsigned_int32()
                    for k in range(num_edges):
                        is_flipped = bool(self.__read_unsigned_int32())
                        edge_index = self.__read_unsigned_int32()

        # Chunk_Materials
        elif chunkid == 4:
            nummaterials = self.__read_unsigned_int32()
            for i in range(nummaterials):
                num_chars = self.__read_unsigned_int32()
                material = self.__read_string(num_chars)
                self.__materials.append(material)

        # Chunk_Triangles
        elif chunkid == 5:
            num_ghost_vertices = self.__read_unsigned_int32()
            for i in range(num_ghost_vertices):
                ghost_vertex = self.__read_vec3_float32()
            num_smoothed_normals = self.__read_unsigned_int32()
            for i in range(num_smoothed_normals):
                smoothed_normal = self.__read_vec3_float32()
            num_faces = self.__read_unsigned_int32()
            num_triangles = self.__read_unsigned_int32()
            for i in range(num_faces):
                num_face_triangles = self.__read_unsigned_int32()
                for j in range(num_face_triangles):
                    vertex_index1 = self.__read_unsigned_int32()
                    vertex_index2 = self.__read_unsigned_int32()
                    vertex_index3 = self.__read_unsigned_int32()
                    smoothed_normal_index1 = self.__read_unsigned_int32()
                    smoothed_normal_index2 = self.__read_unsigned_int32()
                    smoothed_normal_index3 = self.__read_unsigned_int32()

        # Chunk_Facelayers
        elif chunkid == 6:
            num_facelayers = self.__read_unsigned_int32()
            format = self.__read_unsigned_int32()
            if format != 2:
                sys.exit("Error: format is not 2")
            for i in range(num_facelayers):
                has_layers = bool(self.__read_unsigned_int32())
                if has_layers:
                    num_layerbitvalues = self.__read_unsigned_int32()
                    for j in range(num_layerbitvalues):
                        bitmask = self.__read_unsigned_int32()

        # Chunk_Mappinggroups
        elif chunkid == 7:
            num_mappinggroups = self.__read_unsigned_int32()
            for i in range(num_mappinggroups):
                mgid = self.__read_unsigned_int32()
                angle = self.__read_float32()
                scale = self.__read_vec2_float32()
                offset = self.__read_vec2_float32()
                normal = self.__read_vec3_float32()

        # Chunk_Geometrygroups
        elif chunkid == 8:
            num_vertexgroups = self.__read_unsigned_int32()
            for i in range(num_vertexgroups):
                vgid = self.__read_unsigned_int32()
                num_indices = self.__read_unsigned_int32()
                for j in range(num_indices):
                    index = self.__read_unsigned_int32()
            num_edgegroups = self.__read_unsigned_int32()
            for i in range(num_edgegroups):
                egid = self.__read_unsigned_int32()
                num_indices = self.__read_unsigned_int32()
                for j in range(num_indices):
                    index = self.__read_unsigned_int32()
            num_facegroups = self.__read_unsigned_int32()
            for i in range(num_facegroups):
                fgid = self.__read_unsigned_int32()
                num_indices = self.__read_unsigned_int32()
                for j in range(num_indices):
                    index = self.__read_unsigned_int32()

        # Skip unrecognized chunks
        else:
            self.__skipped_chunks_count += 1
            print("Warning: unknown mesh chunk id: %d" % (chunkid))
            data = self.__read_bytes(chunklen)

    def __read_chunk_layers(self, chunkstart, chunklen):
        num_layers = self.__read_unsigned_int32()
        for i in range(num_layers):
            wide_string_len = self.__read_unsigned_int32()
            layer_name = self.__read_string(2 * wide_string_len)
            is_visible = bool(self.__read_unsigned_int32())
            red = self.__read_unsigned_char8()
            green = self.__read_unsigned_char8()
            blue = self.__read_unsigned_char8()
            alpha = self.__read_unsigned_char8()
            color = {"red": red, "green": green, "blue": blue, "alpha": alpha}
            layer_id = self.__read_unsigned_int32()

    def __read_chunk_viewports(self, chunkstart, chunklen):
        wide_string_len = self.__read_unsigned_int32()
        viewports_xml = self.__read_bytes(2 * wide_string_len)

    def __read_chunk_groups(self, chunkstart, chunklen):
        num_groups = self.__read_unsigned_int32()
        for i in range(num_groups):
            wide_string_len = self.__read_unsigned_int32()
            group_name = self.__read_string(2 * wide_string_len)
            is_visible = bool(self.__read_unsigned_int32())
            red = self.__read_unsigned_char8()
            green = self.__read_unsigned_char8()
            blue = self.__read_unsigned_char8()
            alpha = self.__read_unsigned_char8()
            color = {"red": red, "green": green, "blue": blue, "alpha": alpha}
            group_id = self.__read_unsigned_int32()


    def __read_chunk_customcolors(self, chunkstart, chunklen):
        num_colors = self.__read_unsigned_int32()
        for i in range(num_colors):
            red = self.__read_unsigned_char8()
            green = self.__read_unsigned_char8()
            blue = self.__read_unsigned_char8()
            alpha = self.__read_unsigned_char8()
            color = {"red": red, "green": green, "blue": blue, "alpha": alpha}

    def __read_chunk_editorsettings(self, chunkstart, chunklen):
        #joku_id_kait = self.__read_unsigned_int32()
        #joku_pituus_kait = self.__read_unsigned_int32()
        #data = self.__read_unsigned_int32()
        #num_settings = self.__read_unsigned_int32()
        #wide_string_len = self.__read_unsigned_int32()
        #joku_name = self.__read_string(2 * wide_string_len)
        data = self.__read_bytes(chunklen)

    def read_level(self):
        with open(self.__filename, "rb") as f:
            self.__level_data = f.read()

        magicnumber = self.__read_string(3)
        if magicnumber != "LVL":
            sys.exit("Error: file '%s' is not a level file" %
                    (os.path.basename(self.__filename)))

        self.__version = self.__read_unsigned_char8()
        print("Reading level \"" + self.__filename +
              "\" (version " + str(self.__version) + ")")

        while self.__bytesread < len(self.__level_data):
            try:
                chunkid = self.__read_unsigned_int32()
                chunklen = self.__read_unsigned_int32()
                chunkstart = self.__bytesread
                self.__read_chunk(chunkid, chunkstart, chunklen)
            except ReadError as e:
                sys.exit("Error: unexpected end of file!")

        if self.__skipped_chunks_count > 0:
            print("Warning: skipped %d unrecognized chunks" %
                  (self.__skipped_chunks_count))

        entity_count = 0
        for entity_classname, entities in self.__entity_properties.iteritems():
            entity_count += len(entities)
        print("Loaded %d entities." % entity_count)




def main(args):
    if len(args) < 2:
        sys.exit("Usage: %s FILE" % (sys.argv[0]))
    if not os.path.exists(sys.argv[1]):
        sys.exit("Error: file %s was not found!" % (sys.argv[1]))
    filename = sys.argv[1]
    reader = LevelFileReader(filename)
    reader.read_level()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
