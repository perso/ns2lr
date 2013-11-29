from binaryparser import BinaryParser


class ChunkGroupsParser(BinaryParser):

    def __init__(self, data, version):
        super(ChunkGroupsParser, self).__init__(data)
        self.version = version

        self.groups = {}

    def parse(self):
        num_groups = self.read_unsigned_int32()
        for i in range(num_groups):
            wide_string_len = self.read_unsigned_int32()
            group_name = self.read_string(2 * wide_string_len)
            is_visible = bool(self.read_unsigned_int32())
            color = self.read_color()
            group_id = self.read_unsigned_int32()
            self.groups[group_id] = {
                "name": group_name,
                "is_visible": is_visible,
                "color": {
                    "red": color[0],
                    "green": color[1],
                    "blue": color[2],
                    "alpha": color[3]
                }
            }