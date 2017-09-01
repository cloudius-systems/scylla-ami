#!/usr/bin/env python
### Script provided by DataStax.

import urllib2
import os
import re
import shlex
import subprocess
import sys
import time

from exceptions import SystemExit

configfile = '/var/lib/scylla/ami.log'

def getTime():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def appendLog(text):
    with open(configfile, "a") as f:
        f.write(text + "\n")
        print text

def exe(command, log=True, expectError=False, shell=False):
    # Helper function to execute commands and print traces of the command and output for debugging/logging purposes
    process = subprocess.Popen(shlex.split(command), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=shell)
    read = process.communicate()

    if log:
        # Print output on next line if it exists
        if len(read[0]) > 0:
            appendLog('[EXEC] ' + getTime() + ' ' + command + ":\n" + read[0])
        elif len(read[1]) > 0:
            if expectError:
                appendLog('[EXEC:E] ' + getTime() + ' ' + command + ":\n" + read[1])
            else:
                appendLog('[ERROR] ' + getTime() + ' ' + command + ":\n" + read[1])

    if not log or (len(read[0]) == 0 and len(read[1]) == 0):
        appendLog('[EXEC] ' + getTime() + ' ' + command)

    return read

def pipe(command1, command2, log=True):
    # Helper function to execute piping commands and print traces of the commands and output for debugging/logging purposes
    p1 = subprocess.Popen(shlex.split(command1), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split(command2), stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    read = p2.stdout.read()

    if not log:
        read = ""

    # Print output on next line if it exists
    if len(read) > 0:
        appendLog('[PIPE] ' + getTime() + ' ' + command1 + ' | ' + command2 + ":\n" + read)
    else:
        appendLog('[PIPE] ' + getTime() + ' ' + command1 + ' | ' + command2)

    output = p2.communicate()[0]

    if log:
        if read and len(read) > 0:
            appendLog('[PIPE] ' + getTime() + ' ' + command1 + ' | ' + command2 + ":\n" + read)

        if output and len(output[0]) > 0:
            appendLog('[PIPE] ' + getTime() + ' ' + command1 + ' | ' + command2 + ":\n" + output[0])
        if output and len(output[1] > 0):
            appendLog('[PIPE] ' + getTime() + ' ' + command1 + ' | ' + command2 + ":\n" + output[1])

        return output

def debug(infotext):
    appendLog('[DEBUG] ' + getTime() + ' ' + str(infotext))

def info(infotext):
    appendLog('[INFO] ' + getTime() + ' ' + str(infotext))

def warn(infotext):
    appendLog('[WARN] ' + getTime() + ' ' + str(infotext))

def error(infotext):
    appendLog('[ERROR] ' + getTime() + ' ' + str(infotext))

def exception(filename):
    if type(sys.exc_info()[1]) == SystemExit:
        return

    appendLog("[ERROR] %s Exception seen in %s:" % (getTime(),filename))
    import traceback
    appendLog(traceback.format_exc())
    sys.exit(1)
