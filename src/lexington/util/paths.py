from werkzeug.wrappers import Request

from lexington.util.di import depends_on

@depends_on(['environ'])
def get_request(environ):
    return Request(environ)

@depends_on(['request'])
def get_method(request):
    return request.method

@depends_on(['request'])
def get_path(request):
    return request.path

@depends_on(['request'])
def get_query_string(request):
    return request.query_string

@depends_on(['request'])
def get_query(request):
    return request.args

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
