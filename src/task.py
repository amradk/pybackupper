from fabric import Connection
from settings import Settings
from storage import Storage

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