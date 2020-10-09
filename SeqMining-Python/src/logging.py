import sys

DEBUG = 'debug1'
INFO = 'info'
WARN = 'warning'

def log2file(filename, input, type='info'):
    fp = open(filename, 'w')
    if type.lower() == 'debug':
        fp.write('** DEBUG **', input)
    elif type.lower() == 'info':
        fp.write(input)
    fp.close() 


def log(input, type='info'):
    if type.lower() == 'debug':
        print('** DEBUG **', input, end='')
    elif type.lower() == 'warning':
        print('* WARNING *', input, end='')
    elif type.lower() == 'info':
        print(input, end='')
