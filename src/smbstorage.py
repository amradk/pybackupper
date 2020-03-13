from smb.SMBConnection import SMBConnection
from smb.smb_structs import *
from storage import Storage
import socket
import datetime

class SmbStorage(Storage):
    def __init__(self, name, host, share, path, user='', password='', port=139):
        super().__init__(name, path)
        self.share = share
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.name_port = 137
        self.my_hostname = socket.gethostname()
        self.smbcon = SMBConnection(self.user, self.password, self.my_hostname, self.host)
        self.smbcon.connect(self.host)

    def connect(self):
        self.smbcon = SMBConnection(self.user, self.password, self.my_hostname, self.host)
        self.smbcon.connect(self.host)

    def close(self):
        self.smbcon.close()

    def create_dir(self, dir_name):
        smb_dir = self.path + '/' + dir_name
        self.smbcon.createDirectory(self.share, smb_dir)

    def put(self, dir_name, file):
        print('File: ', file)
        #self.shares = self.smbcon.listShares()
        #for s in self.shares:
        #    print(s.name)
        date_str = datetime.datetime.now().strftime("%d-%m-%Y")
        try:
            smb_dir = self.smbcon.getAttributes(self.share, self.path + '/' + dir_name)
            if smb_dir.isDirectory == False:
                self.create_dir(dir_name)
        except OperationFailure:
            self.create_dir(dir_name)

        try:
            smb_dir = self.smbcon.getAttributes(self.share, self.path + '/' + dir_name + '/' + date_str)
            if smb_dir.isDirectory == False:
                self.create_dir(dir_name+'/'+date_str)
        except OperationFailure:
            self.create_dir(dir_name+'/'+date_str)

        data = open(file,'rb')
        file_name = file.split('/')
        file_name = file_name[-1]
        self.smbcon.storeFile(self.share, self.path + '/' + dir_name + '/' + date_str + '/' + file_name, data)
        data.close()