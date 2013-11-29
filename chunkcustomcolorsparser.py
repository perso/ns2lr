from binaryparser import BinaryParser

class ChunkCustomColorsParser(BinaryParser):

    def __init__(self):
        pass

    def parse(self, chunk):
        self.colors = []
        num_colors = self.read_unsigned_int32()
        for i in range(num_colors):
            color = self.read_color()
            self.colors.append({
                "red": color[0], "green": color[1],
                "blue": color[2], "alpha": color[3]
            })