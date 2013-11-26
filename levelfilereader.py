from struct import *
import pprint

from errors import ReadError
from levelparser import LevelParser

class LevelFileReader:

    """Reads NS2 level files"""

    def __init__(self, filename):
        self.filename = filename
        self.entities = []

    def read_level(self):
        parser = LevelParser(self.filename)
        parser.parse()
        for entity in parser.entities:
            self.entities.append(Entity(classname=entity["classname"]))
            pprint.pprint(entity["properties"])

class Entity:

    def __init__(self, classname):
        self.classname = classname
