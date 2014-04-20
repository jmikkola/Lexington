import collections

from werkzeug.wrappers import Response

from lexington.util import di
from lexington.util import route
from lexington.util import view_map
from lexington.util import paths

def default_dependencies(settings):
    dependencies = di.Dependencies()
    dependencies.register_value('settings', settings)
    dependencies.register_value('respond', Response)
    dependencies.register_late_bound_value('environ')
    paths.register_all(dependencies)
    return dependencies

def app():
    """
    Helper function to construct the application factory(!)
    """
    settings = {}
    dependencies = default_dependencies(settings)
    views = view_map.ViewMapFactory()
    routes = route.Routes()
    return ApplicationFactory(settings, dependencies, views, routes)

class ApplicationFactory:
    def __init__(self, settings, dependencies, views, routes):
        self._settings = settings
        self._dependencies = dependencies
        self._views = views
        self._routes = routes

    def add_route(self, route_name, method, path_description):
        self._routes.add_route(route_name, method, path_description)

    def add_view_fn(self, route_name, fn, dependencies=None):
        if dependencies is None:
            dependencies = []
        view = view_map.View(fn, route_name, dependencies)
        self.add_view(view)

    def add_view(self, view):
        self._views.add_view(view)

    def add_value(self, name, value):
        self._dependencies.register_value(name, value)

    def add_factory(self, name, factory_fn, dependencies=None):
        self._dependencies.register_factory(name, factory_fn, dependencies)

    def create_app(self):
        self._dependencies.register_factory(
            'routing',
            self._routes.get_routing,
        )
        self._dependencies.register_factory(
            'route_names',
            lambda routing: routing.get_names(),
            ['routing'],
        )
        self._dependencies.register_factory(
            'provided_dependencies',
            self._dependencies.provided_dependencies,
        )
        self._dependencies.register_factory(
            'view_map',
            self._views.create,
            ['route_names', 'provided_dependencies'],
        )
        self._dependencies.check_dependencies()
        return Application(self._dependencies)

class Application:
    def __init__(self, dependencies):
        self._dependencies = dependencies

    def __call__(self, environ, start_response):
        response = self._get_response(environ)
        return response(environ, start_response)

    def _get_response(self, environ):
        injector = self._dependencies.build_injector(late_bound_values={
            'environ': environ,
        })

        routing = injector.get_dependency('routing')
        view_map = injector.get_dependency('view_map')

        method = injector.get_dependency('method')
        path = injector.get_dependency('path')

        route_name, segment_matches = routing.path_to_route(path, method)
        if route_name is None:
            return self._404('Route not found')

        view = view_map.get_view(route_name)
        if view is None:
            return self._404('No view found for route ' + route_name)

        result = injector.inject(view.fn, view.dependencies)
        if isinstance(result, Response):
            return result
        else: # Assume that the result is text
            return Response(result, mimetype='text/plain')

    def _404(self, message):
        return Response(message, status=404)
