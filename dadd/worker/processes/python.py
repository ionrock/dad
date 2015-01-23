import os

from subprocess import call, STDOUT

from dadd.worker.processes import WorkerProcess


class PythonWorkerProcess(WorkerProcess):

    def install_virtualenv(self):
        if not call(['pip', 'install', 'virtualenv']):
            call(['easy_install', 'virtualenv'])

    def create_virtualenv(self):
        if not call(['virtualenv', 'venv']):
            self.install_virtualenv()
            call(['virtualenv', 'venv'])
        os.environ['PATH'] = os.path.abspath('venv') + ':' + os.environ['PATH']

    def install_python_deps(self):
        self.create_virtualenv()

        # Make sure we have a list
        if isinstance(self.spec['python_deps'], basestring):
            self.spec['python_deps'] = [self.spec['python_deps']]

        for dep in self.spec['python_deps']:
            cmd = ['pip', 'install']

            if self.spec.get('python_cheeseshop'):
                cmd.extend(['-i', self.spec['python_cheeseshop']])

            cmd.append(dep)
            self.log('Running: %s' % ' '.join(cmd))
            call(cmd, stderr=STDOUT, stdout=self.output)

    def setup(self):
        super(PythonWorkerProcess, self).setup()
        if 'python_deps' in self.spec:
            self.install_python_deps()
