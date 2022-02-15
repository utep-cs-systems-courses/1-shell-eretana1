import os, sys, re

# Check for PS1 else set it as $
try:
    sys.ps1
except AttributeError:
    sys.ps1 = "$ "

# Make pipe and fds inheritable
inFd, outFd = os.pipe()
for f in (inFd, outFd):
    os.set_inheritable(f, True)

pid = os.getpid()  # Parent PID

args = ''
while True:
    # Read command from user
    args = input(f'{sys.ps1}').split(" ")

    # Check if user wants to exit
    if args[0] == 'exit':
        sys.exit(2)
            
    # Fork to create child for read command
    os.write(1, ("Fork with PID: %d\n" % pid).encode())
    rc = os.fork()

    if rc < 0:  # Fork has failed
        os.write(2, ("err: Failed to fork with PID: %d\n" % pid).encode())
        sys.exit(1)
    elif rc == 0:  # Child In progress
        if '>' in args or '>>' in args:
            os.close(1)  # redirect child's stdout
            os.open("shell-output.txt", os.O_CREAT | os.O_WRONLY);
            os.set_inheritable(1, True)

        for directory in re.split(":", os.environ['PATH']):  # try each directory in the path
            program = "%s/%s" % (directory, args[0])
            try:
                os.execve(program, args, os.environ)  # try to exec program
            except FileNotFoundError:
                pass

        # Unsuccessful to run program. Display Error
        os.write(2, ("%s command not found.\n" % args[0]).encode())
        sys.exit(1)

    else:  # Parent waits for child to finish
        child_pid = os.wait()
