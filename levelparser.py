import sys
import os
from binaryparser import BinaryParser
from errors import ReadError

from chunkobjectparser import ChunkObjectParser
from chunkmeshparser import ChunkMeshParser
from chunklayersparser import ChunkLayersParser
from chunkviewportparser import ChunkViewportParser
from chunkgroupsparser import ChunkGroupsParser
from chunkcustomcolorsparser import ChunkCustomColorsParser
from chunkeditorsettingsparser import ChunkEditorSettingsParser

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
        if magicnumber != "LVL":
            sys.exit("Error: file '%s' is not a level file" %
                    (os.path.basename(self.filename)))

        self.version = self.parse_version()
        print("Reading level \"" + self.filename +
              "\" (version " + str(self.version) + ")")

        while self.fp < len(self.data):
            try:
                self.read_chunk()
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

    def read_chunk(self):

        chunk_id = self.read_unsigned_int32()
        chunk_length = self.read_unsigned_int32()
        chunk_start = self.fp
        chunk = self.read_bytes(chunk_length)

        if chunk_id == 1:
            parser = ChunkObjectParser(chunk, self.version)
            self.entities.append(parser.parse())
        elif chunk_id == 2:
            parser = ChunkMeshParser(chunk, self.version)
            parser.parse()
        elif chunk_id == 3:
            parser = ChunkLayersParser(chunk, self.version)
            parser.parse()
        elif chunk_id == 4:
            parser = ChunkViewportParser(chunk, self.version)
            parser.parse()
        elif chunk_id == 5:
            parser = ChunkGroupsParser(chunk, self.version)
            parser.parse()
        elif chunk_id == 6:
            parser = ChunkCustomColorsParser(chunk, self.version)
            parser.parse()
        elif chunk_id == 7:
            parser = ChunkEditorSettingsParser(chunk, self.version)
            parser.parse()
        else:
            sys.exit("Error: unknown chunk id: %d" % (chunk_id))
        chunk_bytes_read = self.fp - chunk_start
        chunk_bytes_left = chunk_length - chunk_bytes_read
        if chunk_bytes_left != 0:
            sys.exit("Error: read %d bytes, should be %d bytes" %
                    (chunk_bytes_read, chunk_length))
