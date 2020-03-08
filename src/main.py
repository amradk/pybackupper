import yaml
from fabric import Connection
import socket
import datetime
from settings import Settings
from server import Server
from storage import Storage
from mysqldumptask import MySQLDumpTask
from filetask import FileTask
from smbstorage import SmbStorage

class LocalFsStorage(Storage):
    def __init__(self, name, path):
        super().__init__(name, path)

    def put(self, file):
        pass

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