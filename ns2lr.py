#!/usr/bin/python
# Reads NS2 level file.

import os
import sys
import pprint

from levelreader import LevelReader

def main(args):
    if len(args) < 2:
        sys.exit("Usage: %s FILE" % (sys.argv[0]))
    if not os.path.exists(sys.argv[1]):
        sys.exit("Error: file %s was not found!" % (sys.argv[1]))
    filename = sys.argv[1]

    reader = LevelReader(filename)
    reader.read_level()



if __name__ == "__main__":
    sys.exit(main(sys.argv))
