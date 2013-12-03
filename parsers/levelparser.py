import os
import errors

from parsers.binaryparser import BinaryParser

from parsers.chunkobjectparser import ChunkObjectParser
from parsers.chunkmeshparser import ChunkMeshParser
from parsers.chunklayersparser import ChunkLayersParser
from parsers.chunkviewportparser import ChunkViewportParser
from parsers.chunkgroupsparser import ChunkGroupsParser
from parsers.chunkcustomcolorsparser import ChunkCustomColorsParser
from parsers.chunkeditorsettingsparser import ChunkEditorSettingsParser

class ChunkParser(object):

    def __init__(self, chunk_id, chunk, version):
        self.chunk_parser = None

        print("id: %d, length: %d" % (chunk_id, len(chunk)))

        if chunk_id == 1:
            self.chunk_parser = ChunkObjectParser(chunk, version)
        elif chunk_id == 2:
            self.chunk_parser = ChunkMeshParser(chunk, version)
        elif chunk_id == 3:
            self.chunk_parser = ChunkLayersParser(chunk, version)
        elif chunk_id == 4:
            self.chunk_parser = ChunkViewportParser(chunk, version)
        elif chunk_id == 5:
            self.chunk_parser = ChunkGroupsParser(chunk, version)
        elif chunk_id == 6:
            self.chunk_parser = ChunkCustomColorsParser(chunk, version)
        elif chunk_id == 7:
            self.chunk_parser = ChunkEditorSettingsParser(chunk, version)
        else:
            raise errors.ParseError("Error: unknown chunk id: %d" % (chunk_id))

    def parse_chunk(self):
        return self.chunk_parser.parse()

class LevelParser(BinaryParser):
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename, "rb") as f:
            level_data = f.read()
        super(LevelParser, self).__init__(level_data)
        self.elements = { 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[] }

    def parse(self):
        magicnumber = self.parse_magic_number()
        if magicnumber != "LVL":
            raise errors.TypeError("Error: file '%s' is not a level file" % (os.path.basename(self.filename)))

        self.version = self.parse_version()
        print("Reading level \"" + self.filename +
              "\" (version " + str(self.version) + ")")

        while not self.end():
            try:
                chunk_id = self.read_unsigned_int32()
                chunk_length = self.read_unsigned_int32()
                value = self.read_chunk(chunk_id, chunk_length)
                self.elements[chunk_id].append(value)

            except IOError as e:
                raise

    def parse_magic_number(self):
        return self.read_string(3)

    def parse_version(self):
        return self.read_unsigned_char8()

    def read_chunk(self, chunk_id, chunk_length):
        chunk_start = self.fp
        chunk = self.read_bytes(chunk_length)
        parser = ChunkParser(chunk_id, chunk, self.version)
        value = parser.parse_chunk()
        chunk_bytes_read = self.fp - chunk_start
        chunk_bytes_left = chunk_length - chunk_bytes_read
        if chunk_bytes_left != 0:
            raise errors.ParseError("Error: read %d bytes, should be %d bytes" % (chunk_bytes_read, chunk_length))
        return value

    def get_entities(self):
        return self.elements[1]

    def get_mesh(self):
        return self.elements[2][0]

    def get_layers(self):
        return self.elements[3]

    def get_viewport(self):
        return self.elements[4]

    def get_groups(self):
        if 0 in self.elements[5]:
            return self.elements[5][0]
        else:
            return {}

    def get_customcolors(self):
        return self.elements[6]

    def get_editorsettings(self):
        return self.elements[7]