from struct import *
from errors import ReadError

class BinaryParser(object):

    def __init__(self, data):
        self.data = data
        self.fp = 0

    def read_unsigned_char8(self):
        data = self.read_bytes(1)
        return unpack('B', data)[0]

    def read_unsigned_int32(self):
        data = self.read_bytes(4)
        return unpack('I', data)[0]

    def read_signed_int32(self):
        data = self.read_bytes(4)
        return unpack('i', data)[0]

    def read_float32(self):
        data = self.read_bytes(4)
        return unpack('f', data)[0]

    def read_vec2_float32(self):
        data = self.read_bytes(8)
        return unpack('ff', data)

    def read_vec3_float32(self):
        data = self.read_bytes(12)
        return unpack('fff', data)

    def read_string(self, n):
        data = self.read_bytes(n)
        return data.decode("utf-8")

    def read_color(self):
        data = self.read_bytes(4)
        return unpack('BBBB', data)

    def read_bytes(self, n):
        data = self.data[self.fp:self.fp+n]
        if len(data) < n:
            raise ReadError(
                "Error: expected %d bytes, read %d" % (n, len(data)))
        else:
            self.fp += n
            return data