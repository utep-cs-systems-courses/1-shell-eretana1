#! /usr/bin/env python3

import os, sys, re

def exec_pipe(exec_args, bg_enabled):
    inFd, outFd = os.pipe()
    for fd in (inFd, outFd):
        os.set_inheritable(fd, True)
        
    rc = os.fork()

    if rc < 0:  # Failed fork
        os.write(1, 'Failed to fork.'.encode())
        sys.exit(1)
        
    elif rc == 0:
        os.close(1)
        os.dup(outFd)
        os.set_inheritable(1, True)
        
        # Close all pipes
        for fd in (inFd, outFd):
            os.close(fd)
        exec_program(exec_args[:exec_args.index('|')])
        sys.exit(1)
    else:
        if bg_enabled:
            os.wait()
            
        os.close(0)
        os.dup(inFd)
        os.set_inheritable(0, True)
        # Close fd in pipes
        for fd in (outFd, inFd):
            os.close(fd)
        exec_program(exec_args[exec_args.index('|') + 1:])
        sys.exit(1)

def exec_program(exec_args):
    for directory in re.split(":", os.environ['PATH']):  # try each directory in the path
        program = "%s/%s" % (directory, exec_args[0])
        try:
            os.execve(program, exec_args, os.environ)  # try to exec program
        except FileNotFoundError:
            pass

    # Unsuccessful to run program. Display Error
    os.write(1, ("%s command not found.\n" % args[0]).encode())

    
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
    os.write(1, f'~{os.getcwd()}: {sys.ps1}'.encode())
    args = os.read(0, 1000).decode().split()

    # Check if background tasks enabled and enable args
    bg_enabled = True if '&' in args else False
    args = args[:-1] if bg_enabled else args

    # No user Input exists
    if len(args) == 0:
        continue

    # Check if user wants to exit
    if args[0] == 'exit':
        sys.exit(1)

    # Change current directory
    if args[0] == 'cd':
        if len(args) == 1:
            os.chdir('/')
        else:
            try:
                os.chdir(f'{args[1]}')
            except:
                os.write(1, ('Invalid directory: %s\n' % args[1]).encode())
                
    # Execute pipes
    elif '|' in args:
        exec_pipe(args, bg_enabled)

    else:
        # Fork to create child for read command
        rc = os.fork()

        if rc < 0:  # Fork has failed
            sys.exit(1)
        elif rc == 0:  # Child in progress
            error_state = False

            if '>' in args:
                file_index = args.index('>')
                os.close(1)  # redirect child's stdout
                try:
                    os.open(args[file_index + 1], os.O_CREAT | os.O_WRONLY);
                    os.set_inheritable(1, True)
                    args = args[:file_index]
                except FileNotFoundError:
                    error_state = False
                    os.write(1, ('bash: %s: No such file or directory' % args[file_index + 1]).encode())

            elif '<' in args:
                file_index = args.index('<')
                os.close(0)  # Redirect child's stdin
                try:
                    os.open(args[file_index + 1], os.O_RDONLY)
                    os.set_inheritable(0, True)
                    args = args[:file_index]
                except FileNotFoundError:
                    error_state = True
                    os.write(1, ('bash: %s: No such file or directory \n' % args[file_index + 1]).encode())

            else:
                # If there isn't a command error then execute a program
                if not error_state:
                    exec_program(args)

                # End child process after execution
                sys.exit(1)

        else:  # Parent waits for child to finish
            if bg_enabled is False:
                os.wait()

    

