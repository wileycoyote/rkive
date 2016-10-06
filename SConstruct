import subprocess
import os
import re

def runTests(target = None, source = None, env = None) :
    args=['nosetests','-v','tests']
    tests=[fn for fn in os.listdir('tests') if any([re.match(r'^test.*\.py$', fn)])];
    for t in tests:
        if t in COMMAND_LINE_TARGETS:
            args.append(t)
    # fill args
    env.PrependENVPath('PATH','/home/roger/venv/bin')
    pp = os.path.join(os.getcwd(), 'lib')
    env.PrependENVPath('PYTHONPATH',pp) 
    retCode = subprocess.call(args, env = env['ENV'], cwd = os.getcwd(), shell = True)
    Exit(retCode)

env = Environment()
if 'test' in COMMAND_LINE_TARGETS:
    runTestsCmd = env.Command('runTests', None, Action(runTests, "Running tests"))
    AlwaysBuild(runTestsCmd)
    Alias('test', runTestsCmd)
