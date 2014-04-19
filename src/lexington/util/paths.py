from urllib import parse
from werkzeug.wrappers import Request

from lexington.util.di import depends_on

@depends_on(['environ'])
def get_request(environ):
    return Request(environ)

# TODO: clean up all of these...
@depends_on(['environ'])
def get_method(environ):
    return environ['REQUEST_METHOD']

@depends_on(['environ'])
def get_path(environ):
    return environ['PATH_INFO']

@depends_on(['environ'])
def get_query_string(environ):
    return environ['QUERY_STRING']

@depends_on(['query_string'])
def get_query(query_string):
    return parse.parse_qs(query_string)

def register_all(dependencies):
    dependant_functions = {
        'request': get_request,
        'method': get_method,
        'path': get_path,
        'query_string': get_query_string,
        'query': get_query,
    }
    for name, dependant in dependant_functions.items():
        dependencies.register_dependant(name, dependant)
