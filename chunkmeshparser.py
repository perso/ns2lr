from binaryparser import BinaryParser


class ChunkMeshParser(BinaryParser):

    def __init__(self, data, version):
        super(ChunkMeshParser, self).__init__(data)
        self.version = version

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

    def parse(self):

        while not self.end():

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
                data = self.read_bytes(mesh_chunk_length)

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

