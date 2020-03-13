from task import Task

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