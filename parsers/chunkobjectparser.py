from parsers.binaryparser import BinaryParser
import errors


class ChunkObjectParser(BinaryParser):
    def __init__(self, data, version):
        super(ChunkObjectParser, self).__init__(data)
        self.version = version

    def parse_layerdata(self):
            layerdata = {}
            has_layerdata = bool(self.read_unsigned_int32())
            if has_layerdata:
                layerdata["format"] = self.read_unsigned_int32()
                layerdata["bitvalues"] = []
                num_layerbitvalues = self.read_unsigned_int32()
                for i in range(num_layerbitvalues):
                    bitmask = self.read_unsigned_int32()
                    layerdata["bitvalues"].append(bitmask)
            return layerdata

    def parse_type_float(self, prop_type, num_components):
        prop = None
        components = []
        for i in range(num_components):
            if i < 4:
                # Components beyond the fourth are ignored
                component_value = self.read_float32()
                components.append(component_value)
        if (prop_type in (2, 6, 8, 9)):
            prop = components[0]
        elif (prop_type == 7):
            if len(components) == 3:
                prop = {
                    "roll": components[0],
                    "pitch": components[1],
                    "yaw": components[2]
                }
            elif len(components) == 2:
                prop = {
                    "roll": components[0],
                    "pitch": components[1]
                }
            elif len(components) == 1:
                prop = {
                    "roll": components[0]
                }
            else:
                raise errors.ParseError("Error: Type_Angle requires at least one component.")
        elif (prop_type == 5):
            if len(components) < 4:
                alpha = 1
            else:
                alpha = components[3]
            prop = {
                "red": components[0],
                "green": components[1],
                "blue": components[2],
                "alpha": alpha
            }
        return prop

    def parse(self):

        layerdata = self.parse_layerdata()
        groupid = self.read_unsigned_int32()
        classname_len = self.read_unsigned_int32()
        classname = self.read_string(classname_len)
        properties = {}

        if self.version == 10:
            num_properties = self.read_unsigned_int32()

        while not self.end():

            prop_chunkid = self.read_unsigned_int32()
            if self.version == 10 and (prop_chunkid != 2):
                continue
            prop_chunklen = self.read_unsigned_int32()
            prop_name_len = self.read_unsigned_int32()
            prop_name = self.read_string(prop_name_len)
            prop_type = self.read_unsigned_int32()
            num_components = self.read_unsigned_int32()
            is_animated = bool(self.read_unsigned_int32())

            # Type_Float
            if (prop_type in (2, 5, 6, 7, 8, 9)):

                properties[prop_name] = self.parse_type_float(prop_type, num_components)

            elif (prop_type in (0, 1, 3, 4, 10)):

                if prop_name not in properties:
                    properties[prop_name] = None

                # Type_String
                if (prop_type in (0, 4)):
                    wide_string_len = self.read_unsigned_int32()
                    wide_string_value = self.read_string(2 * wide_string_len)
                    properties[prop_name] = wide_string_value

                # Type_Boolean
                elif (prop_type == 1):
                    boolean_value = bool(self.read_unsigned_int32())
                    properties[prop_name] = boolean_value

                # Type_Integer
                elif (prop_type == 3):
                    integer_value = self.read_signed_int32()
                    properties[prop_name] = integer_value

                # Type_Choice
                elif (prop_type == 10):
                    choice_value = self.read_signed_int32()
                    properties[prop_name] = choice_value

            else:
                raise errors.ParseError("Error: invalid property type: %d" % prop_type)

        entity = {
            "classname": classname,
            "groupid": groupid,
            "layerdata": layerdata,
            "properties": properties
        }

        return entity