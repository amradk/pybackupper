from task import Task

# task to make a backup for files and directories
class FileTask(Task):
    def __init__(self, name, targets, settings):
        super().__init__(name, targets, settings)

    # set command to make archives from files and dir
    def set_archive_command(self):
        if self.settings.archive_type == 'gz':
            self.archive_command = 'tar -czf'

    # build a list of command for further execution
    # mostly to make archives
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

    # clean the temporary directory
    def remote_clean(self):
        for a in self.artifacts:
            self.connection.sudo('rm -rf ' + self.settings.remote_tmp_dir + '/' + a)

    def transfer(self, name):
        #self.storage.connect()
        for a in self.artifacts:
            self.connection.get(self.settings.remote_tmp_dir + '/' + a, self.settings.local_tmp_dir + '/' + a)
            self.storage.put(name, self.settings.local_tmp_dir + '/' + a)
        #self.storage.close()