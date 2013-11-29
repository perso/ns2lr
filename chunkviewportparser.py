class ChunkViewportParser(BinaryParser):

    def __init__(self):
        pass

    def parse(self, chunk):
        wide_string_len = self.read_unsigned_int32()
        viewports_xml = self.read_bytes(2 * wide_string_len)