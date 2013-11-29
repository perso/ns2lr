from parsers.levelparser import LevelParser

class LevelReader(object):

    """Reads NS2 level files"""

    def __init__(self):
        pass

    def read_level(self, filename):
        parser = LevelParser(filename)
        parser.parse()

        # TODO: create objects