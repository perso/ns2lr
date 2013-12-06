import pprint
import errors
from parsers.binaryreader import BinaryReader


class ChunkMeshParser(BinaryReader):

    def __init__(self, data, version):
        super(ChunkMeshParser, self).__init__(data)
        self.version = version

        self.viewport_xml = ""
        self.editor_settings_data = ""

        self.vertices = []
        self.edges = []
        self.faces = []
        self.materials = []
        self.ghost_vertices = []
        self.smoothed_normals = []
        self.triangles = []
        self.face_layers = []
        self.mapping_groups = []
        self.geometry_groups = []

    def parse(self):

        while not self.end():

            mesh_chunk_id = self.read_unsigned_int32()
            mesh_chunk_length = self.read_unsigned_int32()
            mesh_chunk = self.read_bytes(mesh_chunk_length)

            print("\tid: %d, length: %d" % (mesh_chunk_id, len(mesh_chunk)))

            if mesh_chunk_id == 1:
                self.vertices = self.parse_chunk_vertices(mesh_chunk)
            elif mesh_chunk_id == 2:
                self.edges = self.parse_chunk_edges(mesh_chunk)
            elif mesh_chunk_id == 3:
                self.faces = self.parse_chunk_faces(mesh_chunk)
            elif mesh_chunk_id == 4:
                self.materials = self.parse_chunk_materials(mesh_chunk)
            elif mesh_chunk_id == 5:
                (self.ghost_vertices, self.smoothed_normals, self.triangles) = self.parse_chunk_triangles(mesh_chunk)
            elif mesh_chunk_id == 6:
                self.face_layers = self.parse_chunk_facelayers(mesh_chunk)
            elif mesh_chunk_id == 7:
                self.mapping_groups = self.parse_chunk_mappinggroups(mesh_chunk)
            elif mesh_chunk_id == 8:
                self.geometry_groups = self.parse_chunk_geometrygroups(mesh_chunk)
            else:
                print("Warning: unknown mesh chunk id: %d" % (mesh_chunk_id))
                data = self.read_bytes(mesh_chunk_length)

        mesh_data = {
            "vertices": self.vertices,
            "edges": self.edges,
            "faces": self.faces,
            "materials": self.materials,
            "ghost_vertices": self.ghost_vertices,
            "smoothed_normals": self.smoothed_normals,
            "triangles": self.triangles,
            "face_layers": self.face_layers,
            "mapping_groups": self.mapping_groups,
            "geometry_groups": self.geometry_groups
        }
        #pprint.pprint(mesh_data)
        return mesh_data

    def parse_chunk_vertices(self, chunk):
        parser = BinaryReader(chunk)
        vertices = []
        num_vertices = parser.read_unsigned_int32()
        for i in range(num_vertices):
            vec3 = parser.read_vec3_float32()
            has_smoothing = bool(parser.read_unsigned_char8())
            vertices.append({
                "point": {
                    "x": vec3[0],
                    "y": vec3[1],
                    "z": vec3[2]
                },
                "has_smoothing": has_smoothing
            })
        return vertices

    def parse_chunk_edges(self, chunk):
        parser = BinaryReader(chunk)
        edges = []
        num_edges = parser.read_unsigned_int32()
        for i in range(num_edges):
            vi_1 = parser.read_unsigned_int32()
            vi_2 = parser.read_unsigned_int32()
            is_flipped = bool(parser.read_unsigned_char8())
            edges.append({
                "vi_1": vi_1,
                "vi_2": vi_2,
                "is_flipped": is_flipped
            })
        return edges

    def parse_chunk_faces(self, chunk):
        parser = BinaryReader(chunk)
        faces = []
        num_faces = parser.read_unsigned_int32()
        for i in range(num_faces):
            face = {}
            face["angle"] = parser.read_float32()
            face["offset"] = parser.read_vec2_float32()
            face["scale"] = parser.read_vec2_float32()
            face["mapping_group_id"] = parser.read_unsigned_int32()
            face["materialid"] = parser.read_unsigned_int32()
            face["edgeloops"] = []
            num_additional_edgeloops = parser.read_unsigned_int32()
            # border edge loop is always the first edge loop
            face["border_edgeloop"] = self.parse_edgeloop(parser)
            for j in range(num_additional_edgeloops):
                edgeloop = self.parse_edgeloop(parser)
                face["edgeloops"].append(edgeloop)
            faces.append(face)
        return faces

    def parse_edgeloop(self, parser):
        edgeloop = []
        num_edges = parser.read_unsigned_int32()
        for k in range(num_edges):
            is_flipped = bool(parser.read_unsigned_int32())
            edge_index = parser.read_unsigned_int32()
            edge = {
                "edge_index": edge_index,
                "is_flipped": is_flipped
            }
            edgeloop.append(edge)
        return edgeloop

    def parse_chunk_materials(self, chunk):
        parser = BinaryReader(chunk)
        materials = []
        num_materials = parser.read_unsigned_int32()
        for i in range(num_materials):
            num_chars = parser.read_unsigned_int32()
            material = parser.read_string(num_chars)
            materials.append(material)
        return materials

    def parse_chunk_triangles(self, chunk):
        parser = BinaryReader(chunk)
        ghost_vertices = []
        num_ghost_vertices = parser.read_unsigned_int32()
        for i in range(num_ghost_vertices):
            ghost_vertex = parser.read_vec3_float32()
            ghost_vertices.append(ghost_vertex)
        smoothed_normals = []
        num_smoothed_normals = parser.read_unsigned_int32()
        for i in range(num_smoothed_normals):
            smoothed_normal = parser.read_vec3_float32()
            smoothed_normals.append(smoothed_normal)
        triangles = []
        num_faces = parser.read_unsigned_int32()
        num_triangles = parser.read_unsigned_int32()
        for i in range(num_faces):
            triangles.append([])
            num_face_triangles = parser.read_unsigned_int32()
            for j in range(num_face_triangles):
                vertex_index1 = parser.read_unsigned_int32()
                vertex_index2 = parser.read_unsigned_int32()
                vertex_index3 = parser.read_unsigned_int32()
                smoothed_normal_index1 = parser.read_unsigned_int32()
                smoothed_normal_index2 = parser.read_unsigned_int32()
                smoothed_normal_index3 = parser.read_unsigned_int32()
                triangles[i].append({
                    "vi_1": vertex_index1,
                    "vi_2": vertex_index2,
                    "vi_3": vertex_index3,
                    "sni_1": smoothed_normal_index1,
                    "sni_2": smoothed_normal_index2,
                    "sni_3": smoothed_normal_index3
                })
        return (ghost_vertices, smoothed_normals, triangles)

    def parse_chunk_facelayers(self, chunk):
        parser = BinaryParser(chunk)
        facelayers = []
        num_facelayers = parser.read_unsigned_int32()
        format = parser.read_unsigned_int32()
        if format != 2:
            raise errors.ParseError("Error: format is not 2")
        for i in range(num_facelayers):
            facelayers.append([])
            has_layers = bool(parser.read_unsigned_int32())
            if has_layers:
                num_layerbitvalues = parser.read_unsigned_int32()
                for j in range(num_layerbitvalues):
                    bitmask = parser.read_unsigned_int32()
                    facelayers[i].append(bitmask)
        return facelayers

    def parse_chunk_mappinggroups(self, chunk):
        parser = BinaryReader(chunk)
        mappinggroups = {}
        num_mappinggroups = parser.read_unsigned_int32()
        for i in range(num_mappinggroups):
            mgid = parser.read_unsigned_int32()
            angle = parser.read_float32()
            scale = parser.read_vec2_float32()
            offset = parser.read_vec2_float32()
            normal = parser.read_vec3_float32()
            mappinggroups[mgid] = {
                "angle": angle,
                "scale": scale,
                "offset": offset,
                "normal": normal
            }
        return mappinggroups

    def parse_chunk_geometrygroups(self, chunk):
        parser = BinaryReader(chunk)
        vertexgroups = {}
        num_vertexgroups = parser.read_unsigned_int32()
        for i in range(num_vertexgroups):
            vgid = parser.read_unsigned_int32()
            vertexgroups[vgid] = []
            num_indices = parser.read_unsigned_int32()
            for j in range(num_indices):
                index = parser.read_unsigned_int32()
                vertexgroups[vgid].append(index)
        edgegroups = {}
        num_edgegroups = parser.read_unsigned_int32()
        for i in range(num_edgegroups):
            egid = parser.read_unsigned_int32()
            edgegroups[egid] = []
            num_indices = parser.read_unsigned_int32()
            for j in range(num_indices):
                index = parser.read_unsigned_int32()
                edgegroups[egid].append(index)
        facegroups = {}
        num_facegroups = parser.read_unsigned_int32()
        for i in range(num_facegroups):
            fgid = parser.read_unsigned_int32()
            facegroups[fgid] = []
            num_indices = parser.read_unsigned_int32()
            for j in range(num_indices):
                index = parser.read_unsigned_int32()
                facegroups[fgid].append(index)
        return {
            "vertexgroups": vertexgroups,
            "edgegroups": edgegroups,
            "facegroups": facegroups
        }

