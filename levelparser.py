import sys
import os
from binaryparser import BinaryParser
from errors import ReadError

class LevelParser(BinaryParser):
    def __init__(self, filename):

        self.filename = filename
        self.version = 0
        self.skipped_chunks_count = 0

        self.viewport_xml = ""
        self.editor_settings_data = ""

        self.entities = []
        self.vertices = []
        self.edges = []
        self.faces = []
        self.materials = []
        self.ghost_vertices = []
        self.smoothed_normals = []
        self.facelayers = []
        self.customcolors = []

        self.mappinggroups = {}
        self.vertexgroups = {}
        self.edgegroups = {}
        self.facegroups = {}
        self.groups = {}
        self.layers = {}

        with open(self.filename, "rb") as f:
            level_data = f.read()
        super(LevelParser, self).__init__(level_data)

    def parse(self):

        magicnumber = self.parse_magic_number()
        magicnumber == "LVL" or sys.exit("Error: file '%s' is not a level file" % (os.path.basename(self.filename)))
        self.version = self.parse_version()
        print("Reading level \"" + self.filename + "\" (version " + str(self.version) + ")")
        while not self.end():
            try:
                self.read_chunk()
            except ReadError as e:
                sys.exit("Error: unexpected end of file!")
        if self.skipped_chunks_count > 0:
            print("Warning: skipped %d unrecognized chunks" %
                  (self.skipped_chunks_count))

    def parse_magic_number(self):
        return self.read_string(3)

    def parse_version(self):
        return self.read_unsigned_char8()

    def read_chunk(self):
        chunk_id = self.read_unsigned_int32()
        chunk_length = self.read_unsigned_int32()
        chunk_start = self.fp
        chunk = self.read_bytes(chunk_length)

        if chunk_id == 1:
            parser =
        elif chunk_id == 2:
            self.parse_chunk_mesh(chunk_start, chunk_length)
        elif chunk_id == 3:
            self.parse_chunk_layers(chunk_start, chunk_length)
        elif chunk_id == 4:
            self.parse_chunk_viewport(chunk_start, chunk_length)
        elif chunk_id == 5:
            self.parse_chunk_groups(chunk_start, chunk_length)
        elif chunk_id == 6:
            self.parse_chunk_customcolors(chunk_start, chunk_length)
        elif chunk_id == 7:
            self.parse_chunk_editorsettings(chunk_start, chunk_length)
        else:
            self.read_bytes(chunk_length)
            sys.exit("Error: unknown chunk id: %d" % (chunk_id))
        chunk_bytes_read = self.fp - chunk_start
        chunk_bytes_left = chunk_length - chunk_bytes_read
        if chunk_bytes_left != 0:
            sys.exit("Error: read %d bytes, should be %d bytes" %
                    (chunk_bytes_read, chunk_length))

    def parse_layerdata(self):
        layerdata = {}
        has_layerdata = bool(self.read_unsigned_int32())
        if has_layerdata:
            layerdata["format"] = self.read_unsigned_int32()
            layerdata["bitvalues"] = []
            num_layerbitvalues = self.read_unsigned_int32()
            for i in range(num_layerbitvalues):
                bitmask = self.read_unsigned_int32()
                layerdata["bitvalues"].append(bitmask)
        return layerdata

    def parse_type_float(self, prop_type, num_components):
        prop = None
        components = []
        for i in range(num_components):
            if i < 4:
                # Components beyond the fourth are ignored
                component_value = self.read_float32()
                components.append(component_value)
        if (prop_type in (2, 6, 8, 9)):
            prop = components[0]
        elif (prop_type == 7):
            if len(components) == 3:
                prop = {
                    "roll": components[0],
                    "pitch": components[1],
                    "yaw": components[2]
                }
            elif len(components) == 2:
                prop = {
                    "roll": components[0],
                    "pitch": components[1]
                }
            elif len(components) == 1:
                prop = {
                    "roll": components[0]
                }
            else:
                sys.exit("Error: Type_Angle requires at least one component.")
        elif (prop_type == 5):
            if len(components) < 4:
                alpha = 1
            else:
                alpha = components[3]
            prop = {
                "red": components[0],
                "green": components[1],
                "blue": components[2],
                "alpha": alpha
            }
        return prop

    def parse_chunk_object(self, chunk_start, chunk_length):

        layerdata = self.parse_layerdata()
        groupid = self.read_unsigned_int32()
        classname_len = self.read_unsigned_int32()
        classname = self.read_string(classname_len)

        if self.version == 10:
            num_properties = self.read_unsigned_int32()

        properties = {}

        while ((self.fp - chunk_start) < chunk_length):

            prop_chunkid = self.read_unsigned_int32()
            if self.version == 10 and (prop_chunkid != 2):
                continue
            prop_chunklen = self.read_unsigned_int32()
            prop_name_len = self.read_unsigned_int32()
            prop_name = self.read_string(prop_name_len)
            prop_type = self.read_unsigned_int32()
            num_components = self.read_unsigned_int32()
            is_animated = bool(self.read_unsigned_int32())

            # Type_Float
            if (prop_type in (2, 5, 6, 7, 8, 9)):

                properties[prop_name] = self.parse_type_float(prop_type, num_components)

            elif (prop_type in (0, 1, 3, 4, 10)):

                # Type_String
                if (prop_type in (0, 4)):
                    wide_string_len = self.read_unsigned_int32()
                    wide_string_value = self.read_string(2 * wide_string_len)
                    properties[prop_name] = wide_string_value

                # Type_Boolean
                elif (prop_type == 1):
                    boolean_value = bool(self.read_unsigned_int32())
                    properties[prop_name] = boolean_value

                # Type_Integer
                elif (prop_type == 3):
                    integer_value = self.read_signed_int32()
                    properties[prop_name] = integer_value

                # Type_Choice
                elif (prop_type == 10):
                    choice_value = self.read_signed_int32()
                    properties[prop_name] = choice_value

            else:
                sys.exit("Error: invalid property type: %d" % prop_type)

        self.entities.append({
            "classname": classname,
            "groupid": groupid,
            "layerdata": layerdata,
            "properties": properties
        })

    def parse_chunk_mesh(self, chunk_start, chunk_length):
        chunk = self.data[chunk_start:chunk_start+chunk_length]
        while ((self.fp - chunk_start) < chunk_length):

            mesh_chunk_id = self.read_unsigned_int32()
            mesh_chunk_length = self.read_unsigned_int32()
            mesh_chunk_start = self.fp

            if mesh_chunk_id == 1:
                self.parse_chunk_vertices(mesh_chunk_start, mesh_chunk_length)
            elif mesh_chunk_id == 2:
                self.parse_chunk_edges(mesh_chunk_start, mesh_chunk_length)
            elif mesh_chunk_id == 3:
                self.parse_chunk_faces(mesh_chunk_start, mesh_chunk_length)
            elif mesh_chunk_id == 4:
                self.parse_chunk_materials(mesh_chunk_start, mesh_chunk_length)
            elif mesh_chunk_id == 5:
                self.parse_chunk_triangles(mesh_chunk_start, mesh_chunk_length)
            elif mesh_chunk_id == 6:
                self.parse_chunk_facelayers(mesh_chunk_start, mesh_chunk_length)
            elif mesh_chunk_id == 7:
                self.parse_chunk_mappinggroups(mesh_chunk_start, mesh_chunk_length)
            elif mesh_chunk_id == 8:
                self.parse_chunk_geometrygroups(mesh_chunk_start, mesh_chunk_length)
            else:
                self.skipped_chunks_count += 1
                print("Warning: unknown mesh chunk id: %d" % (mesh_chunk_id))
                self.read_bytes(mesh_chunk_length)

    def parse_chunk_vertices(self, chunk_start, chunk_length):
        num_vertices = self.read_unsigned_int32()
        for i in range(num_vertices):
            vec3 = self.read_vec3_float32()
            has_smoothing = bool(self.read_unsigned_char8())
            self.vertices.append({
                "point": {
                    "x": vec3[0],
                    "y": vec3[1],
                    "z": vec3[2]
                },
                "has_smoothing": has_smoothing
            })

    def parse_chunk_edges(self, chunk_start, chunk_length):
        num_edges = self.read_unsigned_int32()
        for i in range(num_edges):
            vi_1 = self.read_unsigned_int32()
            vi_2 = self.read_unsigned_int32()
            is_flipped = bool(self.read_unsigned_char8())
            self.edges.append({
                "vi_1": vi_1,
                "vi_2": vi_2,
                "is_flipped": is_flipped
            })

    def parse_chunk_faces(self, chunk_start, chunk_length):
        num_faces = self.read_unsigned_int32()
        for i in range(num_faces):
            face = {}
            face["angle"] = self.read_float32()
            face["offset"] = self.read_vec2_float32()
            face["scale"] = self.read_vec2_float32()
            face["mapping_group_id"] = self.read_unsigned_int32()
            face["materialid"] = self.read_unsigned_int32()
            face["edgeloops"] = []
            num_additional_edgeloops = self.read_unsigned_int32()
            # border edge loop is always the first edge loop
            for j in range(1 + num_additional_edgeloops):
                face["edgeloops"].append([])
                num_edges = self.read_unsigned_int32()
                for k in range(num_edges):
                    is_flipped = bool(self.read_unsigned_int32())
                    edge_index = self.read_unsigned_int32()
                    face["edgeloops"][j].append({
                        "edge_index": edge_index,
                        "is_flipped": is_flipped
                    })
            self.faces.append(face)

    def parse_chunk_materials(self, chunk_start, chunk_length):
        num_materials = self.read_unsigned_int32()
        for i in range(num_materials):
            num_chars = self.read_unsigned_int32()
            material = self.read_string(num_chars)
            self.materials.append(material)

    def parse_chunk_triangles(self, chunk_start, chunk_length):
        num_ghost_vertices = self.read_unsigned_int32()
        for i in range(num_ghost_vertices):
            ghost_vertex = self.read_vec3_float32()
            self.ghost_vertices.append(ghost_vertex)
        num_smoothed_normals = self.read_unsigned_int32()
        for i in range(num_smoothed_normals):
            smoothed_normal = self.read_vec3_float32()
            self.smoothed_normals.append(smoothed_normal)
        num_faces = self.read_unsigned_int32()
        num_triangles = self.read_unsigned_int32()
        for i in range(num_faces):
            num_face_triangles = self.read_unsigned_int32()
            for j in range(num_face_triangles):
                vertex_index1 = self.read_unsigned_int32()
                vertex_index2 = self.read_unsigned_int32()
                vertex_index3 = self.read_unsigned_int32()
                smoothed_normal_index1 = self.read_unsigned_int32()
                smoothed_normal_index2 = self.read_unsigned_int32()
                smoothed_normal_index3 = self.read_unsigned_int32()
                self.faces[i]["triangles"] = {
                    "vi_1": vertex_index1,
                    "vi_2": vertex_index2,
                    "vi_3": vertex_index3,
                    "sni_1": smoothed_normal_index1,
                    "sni_2": smoothed_normal_index2,
                    "sni_3": smoothed_normal_index3
                }

    def parse_chunk_facelayers(self, chunk_start, chunk_length):
        num_facelayers = self.read_unsigned_int32()
        format = self.read_unsigned_int32()
        if format != 2:
            sys.exit("Error: format is not 2")
        for i in range(num_facelayers):
            self.facelayers.append([])
            has_layers = bool(self.read_unsigned_int32())
            if has_layers:
                num_layerbitvalues = self.read_unsigned_int32()
                for j in range(num_layerbitvalues):
                    bitmask = self.read_unsigned_int32()
                    self.facelayers[i].append(bitmask)

    def parse_chunk_mappinggroups(self, chunk_start, chunk_length):
        num_mappinggroups = self.read_unsigned_int32()
        for i in range(num_mappinggroups):
            mgid = self.read_unsigned_int32()
            angle = self.read_float32()
            scale = self.read_vec2_float32()
            offset = self.read_vec2_float32()
            normal = self.read_vec3_float32()
            self.mappinggroups[mgid] = {
                "angle": angle,
                "scale": scale,
                "offset": offset,
                "normal": normal
            }

    def parse_chunk_geometrygroups(self, chunk_start, chunk_length):
        num_vertexgroups = self.read_unsigned_int32()
        for i in range(num_vertexgroups):
            vgid = self.read_unsigned_int32()
            self.vertexgroups[vgid] = []
            num_indices = self.read_unsigned_int32()
            for j in range(num_indices):
                index = self.read_unsigned_int32()
                self.vertexgroups[vgid].append(index)
        num_edgegroups = self.read_unsigned_int32()
        for i in range(num_edgegroups):
            egid = self.read_unsigned_int32()
            self.edgegroups[egid] = []
            num_indices = self.read_unsigned_int32()
            for j in range(num_indices):
                index = self.read_unsigned_int32()
                self.edgegroups[egid].append(index)
        num_facegroups = self.read_unsigned_int32()
        for i in range(num_facegroups):
            fgid = self.read_unsigned_int32()
            self.facegroups[fgid] = []
            num_indices = self.read_unsigned_int32()
            for j in range(num_indices):
                index = self.read_unsigned_int32()
                self.facegroups[fgid].append(index)

    def parse_chunk_viewport(self, chunk_start, chunk_length):
        wide_string_len = self.read_unsigned_int32()
        viewport_xml = self.read_bytes(2 * wide_string_len)
        self.viewport_xml = viewport_xml

    def parse_chunk_groups(self, chunk_start, chunk_length):
        num_groups = self.read_unsigned_int32()
        for i in range(num_groups):
            wide_string_len = self.read_unsigned_int32()
            group_name = self.read_string(2 * wide_string_len)
            is_visible = bool(self.read_unsigned_int32())
            color = self.read_color()
            group_id = self.read_unsigned_int32()
            self.groups[group_id] = {
                "name": group_name,
                "is_visible": is_visible,
                "color": {
                    "red": color[0],
                    "green": color[1],
                    "blue": color[2],
                    "alpha": color[3]
                }
            }

    def parse_chunk_layers(self, chunk_start, chunk_length):
        num_layers = self.read_unsigned_int32()
        for i in range(num_layers):
            wide_string_len = self.read_unsigned_int32()
            layer_name = self.read_string(2 * wide_string_len)
            is_visible = bool(self.read_unsigned_int32())
            color = self.read_color()
            layer_id = self.read_unsigned_int32()
            self.layers[layer_id] = {
                "name": layer_name,
                "is_visible": is_visible,
                "color": {
                    "red": color[0],
                    "green": color[1],
                    "blue": color[2],
                    "alpha": color[3]
                }
            }

    def parse_chunk_customcolors(self, chunk_start, chunk_length):
        num_colors = self.read_unsigned_int32()
        for i in range(num_colors):
            color = self.read_color()
            self.customcolors.append({
                "red": color[0],
                "green": color[1],
                "blue": color[2],
                "alpha": color[3]
            })

    def parse_chunk_editorsettings(self, chunk_start, chunk_length):
        unknown_field_1 = self.read_unsigned_int32()
        unknown_field_2 = self.read_unsigned_int32()
        unknown_field_3 = self.read_unsigned_int32()
        unknown_field_4 = self.read_unsigned_int32()
        wide_string_len = self.read_unsigned_int32()
        wide_string_value = self.read_string(2 * wide_string_len)
        unknown_field_5 = self.read_unsigned_int32()
        for i in range(unknown_field_5):
            number = self.read_unsigned_int32()
        prop_chunk_id = self.read_unsigned_int32()
        prop_chunk_len = self.read_unsigned_int32()
        while ((self.fp - chunk_start) < chunk_length):
            prop_chunkid = self.read_unsigned_int32()
            #if self.version == 10 and (prop_chunkid != 2):
            #    continue
            prop_chunklen = self.read_unsigned_int32()
            wide_string_len = self.read_unsigned_int32()
            wide_string_value = self.read_bytes(wide_string_len)
            prop_type = self.read_unsigned_int32()
            num_components = self.read_unsigned_int32()
            is_animated = bool(self.read_unsigned_int32())
            prop_value = self.read_float32()
        self.editor_settings_data = self.data[chunk_start:chunk_start+chunk_length]
