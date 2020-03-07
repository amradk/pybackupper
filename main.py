import yaml
from fabric import Connection
from smb.SMBConnection import SMBConnection
from smb.smb_structs import *
import socket
import datetime

class Settings():
    def __init__(self, remote_tmp_dir, local_tmp_dir, archive_type, clean_tmp):
        self.remote_tmp_dir = remote_tmp_dir
        self.local_tmp_dir = local_tmp_dir
        self.archive_type = archive_type
        self.clean_tmp = clean_tmp

class Storage():
    def __init__(self, name, path):
        self.name = name
        self.path = path
        #self.proto = ''
        #self.user = ''
        #self.password = ''
        #self.url = ''

    def put(self, file):
        raise NotImplementedError

class LocalFsStorage(Storage):
    def __init__(self, name, path):
        super().__init__(name, path)

    def put(self, file):
        pass


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
        print('FileName: ', file_name)
        self.smbcon.storeFile(self.share, self.path + '/' + dir_name + '/' + date_str + '/' + file_name, data)
        data.close()


class Job():
    def __init__(self, name, tasks=[]):
        self.name = name
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def prepare_tasks(self):
        for t in self.tasks:
            t.build_commands()

    def execute_tasks(self):
        for t in self.tasks:
            t.execute()

    def set_connection(self, conn):
        for t in self.tasks:
            t.set_connection(conn)

    def set_storage(self, storage):
        for t in self.tasks:
            t.set_storage(storage)

    def transfer_artifacts(self):
        for t in self.tasks:
            t.transfer(self.name)

    def clean(self):
        for t in self.tasks:
            t.clean()

class Task():
    def __init__(self, name, targets, settings, connection=None):
        self.name = name
        self.settings = settings
        self.targets = targets
        self.connection = connection
        self.commands = []
        self.artifacts = []

    def __str__(self):
        return f"{'name': self.name, 'targets': self.targets}"

    def set_storage(self, storage):
        self.storage = storage

    def set_connection(self, connection):
        self.connection = connection

    def build_commands(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def transfer(self):
        raise NotImplementedError

    def remote_clean(self):
        for a in self.artifacts:
            self.connection.run('rm -rf ' + self.settings.remote_tmp_dir + '/' + a)

    def local_clean(self):
        for a in self.artifacts:
            self.connection.run('rm -rf ' + self.settings.local_tmp_dir + '/' + a)

    def clean(self):
        for a in self.artifacts:
            self.connection.sudo('rm -rf ' + self.settings.remote_tmp_dir + '/' + a)
            self.connection.run('rm -rf ' + self.settings.local_tmp_dir + '/' + a)

class FileTask(Task):
    def __init__(self, name, targets, settings):
        super().__init__(name, targets, settings)
    
    def set_archive_command(self):
        if self.settings.archive_type == 'gz':
            self.archive_command = 'tar -czf'

    def build_commands(self):
        self.set_archive_command()
        self.artifacts = []
        for t in self.targets:
            artifact = t.split('/')
            artifact = artifact[-1]
            artifact = artifact + '.tar.' + self.settings.archive_type
            command = self.archive_command + ' ' + self.settings.remote_tmp_dir + '/' + artifact + ' ' + t
            self.commands.append(command)
            self.artifacts.append(artifact)

    def execute(self):
        self.results = []
        for c in self.commands:
            r = self.connection.sudo(c)
            self.results.append(r) 

    def remote_clean(self):
        for a in self.artifacts:
            self.connection.sudo('rm -rf ' + self.settings.remote_tmp_dir + '/' + a)

    def transfer(self, name):
        #self.storage.connect()
        for a in self.artifacts:
            self.connection.get(self.settings.remote_tmp_dir + '/' + a, self.settings.local_tmp_dir + '/' + a)
            self.storage.put(name, self.settings.local_tmp_dir + '/' + a)
        #self.storage.close()

class MySQLDumpTask(Task):
    def __init__(self, name, user, password, host, targets, settings):
        super().__init__(name, targets, settings)
        self.user = user
        self.password = password
        self.host = host
    
    def set_archive_command(self):
        if self.settings.archive_type == 'gz':
            self.archive_command = 'gzip >'

    def build_commands(self):
        self.set_archive_command()
        self.artifacts = []
        dump_command = 'mysqldump -u{} -h{} -p{} --single-transaction --set-gtid-purged=OFF'.format(self.user, self.host, self.password)
        for t in self.targets:
            artifact = t + '.sql.' + self.settings.archive_type
            #dump_command = 'mysqlump -u{} -h{} -p{} --single-transaction --set-gtid-purged=OFF {}'.format(self.user, self.host, self.password, t)
            command = dump_command + ' ' + t + ' | ' + self.archive_command + ' ' + self.settings.remote_tmp_dir + '/' + artifact
            self.commands.append(command)
            self.artifacts.append(artifact)

    def execute(self):
        self.results = []
        for c in self.commands:
            r = self.connection.run(c)
            self.results.append(r)

    def transfer(self, name):
        #self.storage.connect()
        for a in self.artifacts:
            print('MSQL: ',a)
            self.connection.get(self.settings.remote_tmp_dir + '/' + a, self.settings.local_tmp_dir + '/' + a)
            self.storage.put(name, self.settings.local_tmp_dir + '/' + a)
        #self.storage.connect()


class Server():
    def __init__(self, name, user, password='', key=''):
        self.name = name
        self.user = user
        self.password = password
        self.key = key
        self.jobs = []
        self.conn = None

    def __str__(self):
        return f"{'name': self.name}"

    def add_job(self, job):
        self.jobs.append(job)

    def add_storage(self, storage):
        for j in self.jobs:
            j.set_storage(storage)

    def connect(self):
        if self.password != '':
            self.conn = Connection(self.name, self.user, self.password, connect_kwargs={
            "key_filename": self.key,})
        else:
            self.conn = Connection(self.name, self.user, connect_kwargs={"key_filename": self.key,})
        
        for j in self.jobs:
            j.set_connection(self.conn)

    def prepare(self):
        if len(self.jobs) > 0:
            for j in self.jobs:
                j.prepare_tasks()

    def execute_jobs(self):
        for j in self.jobs:
            j.execute_tasks()

    def transfer_artifacts(self):
        for j in self.jobs:
            j.transfer_artifacts()

    def clean(self):
        for j in self.jobs:
            j.clean()



def main():
    conf_f = open('conf.yaml', 'r')
    config = yaml.safe_load(conf_f)
    conf_f.close()
    servers = {}
    print(config)
    

    settings = Settings(config['config']['remote_tmp_dir'], config['config']['remote_tmp_dir'], config['config']['archive_type'], True)
    store = SmbStorage(config['store'][0]['name'], config['store'][0]['host'], config['store'][0]['share'], config['store'][0]['path'], config['store'][0]['user'], config['store'][0]['password'])
    for s in config['servers']:
        servers[s['name']] = Server(s['name'], s['user'], password='', key=s['key'])
        for j in config['jobs']:
            job = Job(j['name'])
            for t in j['tasks']:
                if t['type'] == 'dir':
                    job.add_task(FileTask(t['name'], t['target_list'], settings))
                if t['type'] == 'mysql':
                    job.add_task(MySQLDumpTask(t['name'], t['user'], t['password'], t['host'], t['target_list'], settings))
            #tasks[t['name']].execute()
            #tasks[t['name']].transfer()
            #task[t['name']].clean()
            print('Job: ', job.name)
            if job.name in s['jobs']:
                servers[s['name']].add_job(job)

    #execute
    for s in servers.keys():
        servers[s].connect()
        servers[s].prepare()
        servers[s].execute_jobs()
        servers[s].add_storage(store)
        servers[s].transfer_artifacts()
        servers[s].clean()



if __name__ == '__main__':
    main()