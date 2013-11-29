from binaryparser import BinaryParser
import exceptions

class ChunkObjectParser(BinaryParser):
    def __init__(self):
        self.entities = []

    def parse(self, chunk):

        layerdata = {}
        has_layerdata = bool(self.read_unsigned_int32())
        if has_layerdata:
            layerdata["format"] = self.read_unsigned_int32()
            layerdata["bitvalues"] = []
            num_layerbitvalues = self.read_unsigned_int32()
            for i in range(num_layerbitvalues):
                bitmask = self.read_unsigned_int32()
                layerdata["bitvalues"].append(bitmask)

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

                if prop_name not in properties:
                    properties[prop_name] = []

                components = []

                for i in range(num_components):
                    if i < 4:
                        # Components beyond the fourth are ignored
                        component_value = self.read_float32()
                        components.append(component_value)

                # Next the components are assigned based on the type of
                # property

                # Type_Real, Type_Percentage, Type_Time, and Type_Distance use
                # only the first component
                if (prop_type in (2, 6, 8, 9)):
                    properties[prop_name] = components[0]

                # Type_Angle uses component 1 for roll, component 2 for pitch,
                # and component 3 for yaw
                if (prop_type == 7):

                    if len(components) == 3:
                        properties[prop_name].append({
                            "roll": components[0],
                            "pitch": components[1],
                            "yaw": components[2]
                        })
                    elif len(components) == 2:
                        properties[prop_name].append({
                            "roll": components[0],
                            "pitch": components[1]
                        })
                    elif len(components) == 1:
                        properties[prop_name].append({
                            "roll": components[0]
                        })
                    else:
                        raise exceptions.ParseError("Error: Type_Angle requires at least one component.")

                # Type_Color uses component 1 for red, component 2 for green,
                # component 3 for blue, and component 4 for alpha
                # (alpha defaults to 1 if there is no component 4)
                if (prop_type == 5):
                    if len(components) < 4:
                        alpha = 1
                    else:
                        alpha = components[3]
                    properties[prop_name].append({
                        "red": components[0],
                        "green": components[1],
                        "blue": components[2]
                    })

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
                raise exceptions.ParseError("Error: invalid property type: %d" % prop_type)

        self.entities.append({
            "classname": classname,
            "groupid": groupid,
            "layerdata": layerdata,
            "properties": properties
        })

        return self.entities