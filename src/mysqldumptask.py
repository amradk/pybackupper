from task import Task

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