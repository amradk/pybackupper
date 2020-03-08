from fabric import Connection
from job import Job
from storage import Storage


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