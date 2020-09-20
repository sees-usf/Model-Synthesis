import sys

DEBUG = 'debug'
INFO = 'info'

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
    elif type.lower() == 'info':
        print(input, end='')
