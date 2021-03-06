from parsers.binaryreader import BinaryReader


class ChunkViewportParser(BinaryReader):

    def __init__(self, data, version):
        super(ChunkViewportParser, self).__init__(data)
        self.version = version
        self.viewport_xml = ""

    def parse(self):
        wide_string_len = self.read_unsigned_int32()
        viewport_xml = self.read_widestring(2 * wide_string_len)
        self.viewport_xml = viewport_xml
        return viewport_xml