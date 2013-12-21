from parsers.binaryreader import BinaryReader


class ChunkLayersParser(BinaryReader):

    def __init__(self, data, version):
        super(ChunkLayersParser, self).__init__(data)
        self.version = version
        self.layers = {}

    def parse(self):
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
        return self.layers