from binaryparser import BinaryParser


class ChunkCustomColorsParser(BinaryParser):

    def __init__(self, data, version):
        super(ChunkCustomColorsParser, self).__init__(data)
        self.version = version

        self.customcolors = []

    def parse(self):
        num_colors = self.read_unsigned_int32()
        for i in range(num_colors):
            color = self.read_color()
            self.customcolors.append({
                "red": color[0],
                "green": color[1],
                "blue": color[2],
                "alpha": color[3]
            })