from struct import *
import io
from errors import IOError
import errors


class BinaryWriter(object):

    def __init__(self, filename):
        self.stream = io.open(filename, "wb")

    def seek(self, offset):
        self.stream.seek(offset)

    def write_unsigned_char8(self, data):
        packed = pack('B', data)
        self.stream.write(packed)

    def write_unsigned_int32(self, data):
        packed = pack('I', data)
        self.stream.write(packed)

    def write_signed_int32(self, data):
        packed = pack('i', data)
        self.stream.write(packed)

    def write_float32(self, data):
        packed = pack('f', data)
        self.stream.write(packed)

    def write_vec2_float32(self, data):
        packed = pack('ff', data)
        self.stream.write(packed)

    def read_vec3_float32(self, data):
        packed = pack('fff', data)
        self.stream.write(packed)

    def write_string(self, data):
        encoded = data.encode("utf-8")
        self.stream.write(encoded)

    def read_widestring(self, data):
        encoded = data.encode("utf-16")
        self.stream.write(encoded)

    def read_color(self, data):
        packed = pack('BBBB', data)
        self.stream.write(packed)

    def write_bytes(self, data):
        self.stream.write(data)
