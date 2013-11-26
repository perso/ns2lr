class Error(Exception):
    pass

class ReadError(Error):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class WriteError(Error):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
