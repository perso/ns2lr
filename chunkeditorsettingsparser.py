class ChunkEditorSettingsParser(BinaryParser):

    def __init__(self):
        pass

    def parse(self, chunk):
        unknown_field_1 = self.read_unsigned_int32()
        unknown_field_2 = self.read_unsigned_int32()
        unknown_field_3 = self.read_unsigned_int32()
        unknown_field_4 = self.read_unsigned_int32()
        wide_string_len = self.read_unsigned_int32()
        wide_string_value = self.read_string(2 * wide_string_len)
        unknown_field_5 = self.read_unsigned_int32()
        for i in range(unknown_field_5):
            number = self.read_unsigned_int32()
        prop_chunk_id = self.read_unsigned_int32()
        prop_chunk_len = self.read_unsigned_int32()
        while ((self.fp - chunk_start) < chunk_length):
            prop_chunkid = self.read_unsigned_int32()
            #if self.version == 10 and (prop_chunkid != 2):
            #    continue
            prop_chunklen = self.read_unsigned_int32()
            wide_string_len = self.read_unsigned_int32()
            wide_string_value = self.read_bytes(wide_string_len)
            prop_type = self.read_unsigned_int32()
            num_components = self.read_unsigned_int32()
            is_animated = bool(self.read_unsigned_int32())
            prop_value = self.read_float32()