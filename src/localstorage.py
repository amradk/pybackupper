import os
import pathlib
import shutil
from storage import Storage
import datetime

class LocalStorage(Storage):
    def __init__(self, name, path):
        super().__init__(name, path)
        self.path = path

    def create_dir(self, path):
        pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

    def put(self, dir_name, file):
        print('File: ', file)
        #self.shares = self.smbcon.listShares()
        #for s in self.shares:
        #    print(s.name)
        date_str = datetime.datetime.now().strftime("%d-%m-%Y")
        file_name = file.split('/')
        file_name = file_name[-1]
        dest_dir = self.path + '/' + dir_name + '/' + date_str
        self.create_dir(dest_dir)
        shutil.move(file, dest_dir)
