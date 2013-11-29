class ChunkLayersParser(BinaryParser):

    def __init__(self):
        pass

    def parse(self, chunk):
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