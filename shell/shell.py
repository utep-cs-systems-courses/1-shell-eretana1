import os, sys, re

try:
    sys.ps1
except AttributeError:
    sys.ps1 = "$ "

    
# Make pipe and ffds inheritable
inFd, outFd = os.pipe()
for f in (inFd, outFd):
    os.set_inheritable(f, True)

pid = os.getpid()
os.write(1, ("Fork with PID: %d" % pid).encode())
rc = os.fork()

if rc < 0:  # Fork has failed
    os.write(2, ("Failed to fork with PID: %d" % pid).encode())
    sys.exit(1)
elif rc == 0:
    # code here
    
else:
        child_pid = os.wait()
        os.write(1, "Child PID: %d terminated with exit code)

cmd = ''
while cmd != 'exit':
    cmd = input(f'{sys.ps1}')
