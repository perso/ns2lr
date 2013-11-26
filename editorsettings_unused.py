            # Unknown
            editorsettings_chunkid = self.__read_unsigned_int32()
            editorsettings_chunklen = self.__read_unsigned_int32()
            joku_value_3 = self.__read_unsigned_int32()
            joku_value_4 = self.__read_unsigned_int32()
            #print(joku_value_3)
            #print(joku_value_4)
            wide_string_len = self.__read_unsigned_int32()
            wide_string_value = self.__read_string(2 * wide_string_len)
            num_some_weird_numbers = self.__read_unsigned_int32()
            for i in range(num_some_weird_numbers):
                number = self.__read_unsigned_int32()
            prop_chunk_id = self.__read_unsigned_int32()
            prop_chunk_len = self.__read_unsigned_int32()
            while ((self.__bytesread - chunkstart) < chunklen):
                prop_chunkid = self.__read_unsigned_int32()
                if self.__version == 10 and (prop_chunkid != 2):
                    continue
                prop_chunklen = self.__read_unsigned_int32()
                wide_string_len = self.__read_unsigned_int32()
                wide_string_value = self.__read_bytes(wide_string_len)
                prop_type = self.__read_unsigned_int32()
                num_components = self.__read_unsigned_int32()
                is_animated = bool(self.__read_unsigned_int32())
                prop_value = self.__read_float32()