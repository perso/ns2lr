class Error(Exception):
    pass

class IOError(Error):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ParseError(Error):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class TypeError(Error):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)