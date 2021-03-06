import os

from dadd.worker.processes import WorkerProcess
from dadd.worker.utils import printf, call_cmd


class PythonWorkerProcess(WorkerProcess):
    python_dep_dir = 'dadd-pyenv'

    def create_virtualenv(self, name='dadd-worker-venv'):
        printf('Creating the virtualenv', self.output)
        if call_cmd(['virtualenv', name], self.output):
            self.log('Error creating virtualenv')

        venv_bin = os.path.abspath(os.path.join(name, 'bin'))
        # os.environ['PATH'] = venv_bin + ':' + os.environ['PATH']
        os.environ['PYTHONUSERBASE'] = name
        # self.log('Updated Path: %s' % os.environ['PATH'])
        return venv_bin

    def create_pyenv(self):
        dirname = os.path.abspath(self.python_dep_dir)
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        return dirname

    def install_python_deps(self):
        venv = self.create_virtualenv()

        # Make sure we have a list
        if isinstance(self.spec['python_deps'], basestring):
            self.spec['python_deps'] = [self.spec['python_deps']]

        for dep in self.spec['python_deps']:
            # We don't get an updated PATH value when calling in the
            # same process. We need to explicitly call the
            # virtualenv's pip in order to ensure the correct
            # virtualenv is used.
            cmd = [os.path.join(venv, 'pip'), '--user', 'install']

            if self.spec.get('python_cheeseshop'):
                cmd.extend(['-i', self.spec['python_cheeseshop']])

            # a dep might be specific to a cheeseshop, so we are
            # implicitly allowing a dependency to do something like:
            #
            #   `-i http://mycheese.net mypkg>=3.0`
            #
            # We want each arg to be passed to the comand.
            cmd.extend(dep.split())
            self.log('Running: %s' % ' '.join(cmd))
            call_cmd(cmd, self.output)

    def setup(self):
        super(PythonWorkerProcess, self).setup()
        if 'python_deps' in self.spec:
            self.install_python_deps()
