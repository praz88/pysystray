import thread

__all__ = ['threaded', 'DEFAULT_HANDLER']

def default_handler(s):
    ''' Default handler for _App events. Does Nothing '''
    return
    
DEFAULT_HANDLER = default_handler 

def threaded(func):
    def wrapper(*args):
        thread.start_new_thread(func, tuple(args))
    return wrapper       

