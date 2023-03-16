import sys
import inspect


DEBUG = 'debug1'
# DEBUG = 'debug'
INFO = 'info'
WARN = 'warning'

#@ return the object.function name where this function is called.
def whoami():
    stack = inspect.stack()
    the_class = stack[1][0].f_locals["self"].__class__.__name__
    the_method = stack[1][0].f_code.co_name

    return the_class + ':' + the_method

    # callerObj = inspect.currentframe().f_back.f_locals['self']
    # callerFunc = inspect.stack()[1][3]
    # return str(callerObj) +':'+callerFunc


#@ return the line number where this function is called.
def line_numb():
   '''Returns the current line number in our program'''
   return inspect.currentframe().f_back.f_lineno


def log2file(filename, input, type='info'):
    try:
        fp = open(filename, 'w')
    except IOError as e:
        print("Couldn't open file (%s)." % e)
        return

    if type.lower() == 'debug':
        fp.write('* DEBUG *', input)
    elif type.lower() == 'warning':
        print('** WARNING **', input, end='')
    elif type.lower() == 'info':
        fp.write(input)
    fp.close() 


def log(inp, type='info', stop=False):
    if type.lower() == 'debug':
        print('* DEBUG *', inp, end='', flush=True)
        if stop: input('Stop, hit a key to continue ->')
    elif type.lower() == 'warning':
        print('** WARNING **', inp, end='', flush=True)
        if stop: input('Stop, hit a key to continue ->')
    elif type.lower() == 'info':
        print(inp, end='', flush=True)
        if stop: input('Stop, hit a key to continue ->')



