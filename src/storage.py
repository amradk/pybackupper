# base class to different storages

class Storage():
    def __init__(self, name, path):
        self.name = name
        self.path = path
        #self.proto = ''
        #self.user = ''
        #self.password = ''
        #self.url = ''

    def put(self, dir_name, file):
        raise NotImplementedError