import os, pexpect, pytest, sys

DIR = os.path.dirname(__file__)
EXCLUDES = ("__pycache__",)

@pytest.mark.parametrize("directory", [n for n in os.listdir(DIR)
                                       if os.path.isdir(os.path.join(DIR, n)) and n not in EXCLUDES])
def test(directory):
    print

    test_dir = os.path.join(DIR, directory)
    test_spec = os.path.join(test_dir, "test.spec")

    if os.path.exists(test_spec):
        with open(test_spec) as fd:
            ops = fd.read()
    else:
        ops = "RUN forge deploy"

    runner = Runner(os.path.join(DIR, directory), ops)
    runner.run()

class Runner(object):

    def __init__(self, cwd, spec):
        self.cwd = cwd
        self.spec = spec
        self.child = None

    def run(self):
        for line in self.spec.splitlines():
            for stmt in line.split(";"):
                op, arg = stmt.split(None, 1)
                attr = getattr(self, "do_%s" % op, None)
                if attr is None:
                    assert False, "unrecognized op: %s" % op
                else:
                    attr(arg)
        self.wait()

    def wait(self):
        if self.child is not None:
            self.child.expect(pexpect.EOF)
            assert self.child.wait() == 0

    def do_RUN(self, arg):
        self.wait()
        print "RUN", arg
        self.child = pexpect.spawn(arg, cwd=self.cwd)
        self.child.logfile = sys.stdout

    def do_OUT(self, arg):
        self.child.expect_exact(arg.strip())

    def do_TYPE(self, arg):
        if arg.strip().lower() == "<enter>":
            self.child.sendline()
        else:
            self.child.sendline(arg)
