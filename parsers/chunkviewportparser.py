from parsers.binaryparser import BinaryParser


class ChunkViewportParser(BinaryParser):

    def __init__(self, data, version):
        super(ChunkViewportParser, self).__init__(data)
        self.version = version

        self.viewport_xml = ""

    def parse(self):
        wide_string_len = self.read_unsigned_int32()
        viewport_xml = self.read_bytes(2 * wide_string_len)
        self.viewport_xml = viewport_xml