import sys
import pprint
from binaryparser import BinaryParser
from errors import ReadError

class LevelParser(BinaryParser):
    def __init__(self, filename):
        self.filename = filename
        self.version = 0
        self.skipped_chunks_count = 0
        self.materials = []
        self.entities = []
        with open(self.filename, "rb") as f:
            level_data = f.read()
        super(LevelParser, self).__init__(level_data)

    def parse(self):
        magicnumber = self.parse_magic_number()
        if magicnumber != "LVL":
            sys.exit("Error: file '%s' is not a level file" %
                    (os.path.basename(self.filename)))

        self.version = self.parse_version()
        print("Reading level \"" + self.filename +
              "\" (version " + str(self.version) + ")")

        while self.fp < len(self.data):
            try:
                chunkid = self.read_unsigned_int32()
                self.read_chunk(chunkid)
            except ReadError as e:
                sys.exit("Error: unexpected end of file!")

        if self.skipped_chunks_count > 0:
            print("Warning: skipped %d unrecognized chunks" %
                  (self.skipped_chunks_count))

        print("Loaded %d entities." % len(self.entities))

    def parse_magic_number(self):
        return self.read_string(3)

    def parse_version(self):
        return self.read_unsigned_char8()

    def read_chunk(self, chunkid):

        chunk_length = self.read_unsigned_int32()
        chunk_start = self.fp

        if chunkid == 1:
            self.parse_chunk_object(chunk_start, chunk_length)
        elif chunkid == 2:
            self.parse_chunk_mesh(chunk_start, chunk_length)
        elif chunkid == 3:
            self.parse_chunk_layers(chunk_start, chunk_length)
        elif chunkid == 4:
            self.parse_chunk_viewport(chunk_start, chunk_length)
        elif chunkid == 5:
            self.parse_chunk_groups(chunk_start, chunk_length)
        elif chunkid == 6:
            self.parse_chunk_customcolors(chunk_start, chunk_length)
        elif chunkid == 7:
            self.parse_chunk_editorsettings(chunk_start, chunk_length)
        else:
            sys.exit("Error: unknown chunk id: %d" % (chunkid))
            data = self.read_bytes(chunk_length)
        chunk_bytes_read = self.fp - chunk_start
        chunk_bytes_left = chunk_length - chunk_bytes_read
        if chunk_bytes_left != 0:
            sys.exit("Error: read %d bytes, should be %d bytes" %
                    (chunk_bytes_read, chunk_length))

    def parse_chunk_object(self, chunk_start, chunk_length):

        layerdata = {}
        has_layerdata = bool(self.read_unsigned_int32())
        if has_layerdata:
            layerdata["format"] = self.read_unsigned_int32()
            layerdata["bitvalues"] = []
            num_layerbitvalues = self.read_unsigned_int32()
            for i in range(num_layerbitvalues):
                bitmask = self.read_unsigned_int32()
                layerdata["bitvalues"].append(bitmask)

        groupid = self.read_unsigned_int32()
        classname_len = self.read_unsigned_int32()
        classname = self.read_string(classname_len)
        properties = {}

        if self.version == 10:
            num_properties = self.read_unsigned_int32()

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

                if prop_name not in properties:
                    properties[prop_name] = []

                components = []

                for i in range(num_components):
                    if i < 4:
                        # Components beyond the fourth are ignored
                        component_value = self.read_float32()
                        components.append(component_value)

                # Next the components are assigned based on the type of
                # property

                # Type_Real, Type_Percentage, Type_Time, and Type_Distance use
                # only the first component
                if (prop_type in (2, 6, 8, 9)):
                    properties[prop_name] = components[0]

                # Type_Angle uses component 1 for roll, component 2 for pitch,
                # and component 3 for yaw
                if (prop_type == 7):

                    if len(components) == 3:
                        properties[prop_name].append({
                            "roll": components[0],
                            "pitch": components[1],
                            "yaw": components[2]
                        })
                    elif len(components) == 2:
                        properties[prop_name].append({
                            "roll": components[0],
                            "pitch": components[1]
                        })
                    elif len(components) == 1:
                        properties[prop_name].append({
                            "roll": components[0]
                        })
                    else:
                        sys.exit("Error: Type_Angle requires at least one component.")

                # Type_Color uses component 1 for red, component 2 for green,
                # component 3 for blue, and component 4 for alpha
                # (alpha defaults to 1 if there is no component 4)
                if (prop_type == 5):
                    if len(components) < 4:
                        alpha = 1
                    else:
                        alpha = components[3]
                    properties[prop_name].append({
                        "red": components[0],
                        "green": components[1],
                        "blue": components[2]
                    })

            elif (prop_type in (0, 1, 3, 4, 10)):

                if prop_name not in properties:
                    properties[prop_name] = None

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

            chunkid = self.read_unsigned_int32()
            chunklen = self.read_unsigned_int32()
            chunkstart = self.fp

            if chunkid == 1:
                self.parse_chunk_vertices(chunk_start, chunk_length)
            elif chunkid == 2:
                self.parse_chunk_edges(chunk_start, chunk_length)
            elif chunkid == 3:
                self.parse_chunk_faces(chunk_start, chunk_length)
            elif chunkid == 4:
                self.parse_chunk_materials(chunk_start, chunk_length)
            elif chunkid == 5:
                self.parse_chunk_triangles(chunk_start, chunk_length)
            elif chunkid == 6:
                self.parse_chunk_facelayers(chunk_start, chunk_length)
            elif chunkid == 7:
                self.parse_chunk_mappinggroups(chunk_start, chunk_length)
            elif chunkid == 8:
                self.parse_chunk_geometrygroups(chunk_start, chunk_length)
            else:
                self.skipped_chunks_count += 1
                print("Warning: unknown mesh chunk id: %d" % (chunkid))
                data = self.read_bytes(chunklen)

    def parse_chunk_vertices(self, chunk_start, chunk_length):
        num_vertices = self.read_unsigned_int32()
        for i in range(num_vertices):
            vec3 = self.read_vec3_float32()
            smoothing = bool(self.read_unsigned_char8())

    def parse_chunk_edges(self, chunk_start, chunk_length):
        num_edges = self.read_unsigned_int32()
        for i in range(num_edges):
            vi_1 = self.read_unsigned_int32()
            vi_2 = self.read_unsigned_int32()
            is_flipped = bool(self.read_unsigned_char8())

    def parse_chunk_faces(self, chunk_start, chunk_length):
        num_faces = self.read_unsigned_int32()
        for i in range(num_faces):
            angle = self.read_float32()
            offset = self.read_vec2_float32()
            scale = self.read_vec2_float32()
            mapping_group_id = self.read_unsigned_int32()
            materialid = self.read_unsigned_int32()
            additional_edgeloops = self.read_unsigned_int32()
            # account for border edgeloop
            for j in range(1 + additional_edgeloops):
                num_edges = self.read_unsigned_int32()
                for k in range(num_edges):
                    is_flipped = bool(self.read_unsigned_int32())
                    edge_index = self.read_unsigned_int32()

    def parse_chunk_materials(self, chunk_start, chunk_length):
        nummaterials = self.read_unsigned_int32()
        for i in range(nummaterials):
            num_chars = self.read_unsigned_int32()
            material = self.read_string(num_chars)
            self.materials.append(material)

    def parse_chunk_triangles(self, chunk_start, chunk_length):
        num_ghost_vertices = self.read_unsigned_int32()
        for i in range(num_ghost_vertices):
            ghost_vertex = self.read_vec3_float32()
        num_smoothed_normals = self.read_unsigned_int32()
        for i in range(num_smoothed_normals):
            smoothed_normal = self.read_vec3_float32()
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

    def parse_chunk_facelayers(self, chunk_start, chunk_length):
        num_facelayers = self.read_unsigned_int32()
        format = self.read_unsigned_int32()
        if format != 2:
            sys.exit("Error: format is not 2")
        for i in range(num_facelayers):
            has_layers = bool(self.read_unsigned_int32())
            if has_layers:
                num_layerbitvalues = self.read_unsigned_int32()
                for j in range(num_layerbitvalues):
                    bitmask = self.read_unsigned_int32()

    def parse_chunk_mappinggroups(self, chunk_start, chunk_length):
        num_mappinggroups = self.read_unsigned_int32()
        for i in range(num_mappinggroups):
            mgid = self.read_unsigned_int32()
            angle = self.read_float32()
            scale = self.read_vec2_float32()
            offset = self.read_vec2_float32()
            normal = self.read_vec3_float32()

    def parse_chunk_geometrygroups(self, chunk_start, chunk_length):
        num_vertexgroups = self.read_unsigned_int32()
        for i in range(num_vertexgroups):
            vgid = self.read_unsigned_int32()
            num_indices = self.read_unsigned_int32()
            for j in range(num_indices):
                index = self.read_unsigned_int32()
        num_edgegroups = self.read_unsigned_int32()
        for i in range(num_edgegroups):
            egid = self.read_unsigned_int32()
            num_indices = self.read_unsigned_int32()
            for j in range(num_indices):
                index = self.read_unsigned_int32()
        num_facegroups = self.read_unsigned_int32()
        for i in range(num_facegroups):
            fgid = self.read_unsigned_int32()
            num_indices = self.read_unsigned_int32()
            for j in range(num_indices):
                index = self.read_unsigned_int32()

    def parse_chunk_viewport(self, chunk_start, chunk_length):
        wide_string_len = self.read_unsigned_int32()
        viewports_xml = self.read_bytes(2 * wide_string_len)

    def parse_chunk_layers(self, chunk_start, chunk_length):
        num_layers = self.read_unsigned_int32()
        for i in range(num_layers):
            wide_string_len = self.read_unsigned_int32()
            layer_name = self.read_string(2 * wide_string_len)
            is_visible = bool(self.read_unsigned_int32())
            color = self.read_color()
            c = {
                "red": color[0], "green": color[1],
                "blue": color[2], "alpha": color[3]
            }
            layer_id = self.read_unsigned_int32()

    def parse_chunk_customcolors(self, chunk_start, chunk_length):
        self.colors = []
        num_colors = self.read_unsigned_int32()
        for i in range(num_colors):
            color = self.read_color()
            self.colors.append({
                "red": color[0], "green": color[1],
                "blue": color[2], "alpha": color[3]
            })

    def parse_chunk_groups(self, chunk_start, chunk_length):
        num_groups = self.read_unsigned_int32()
        for i in range(num_groups):
            wide_string_len = self.read_unsigned_int32()
            group_name = self.read_string(2 * wide_string_len)
            is_visible = bool(self.read_unsigned_int32())
            color = self.read_color()
            c = {
                "red": color[0], "green": color[1],
                "blue": color[2], "alpha": color[3]
            }
            group_id = self.read_unsigned_int32()

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
