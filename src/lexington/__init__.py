import collections

from werkzeug.wrappers import Response

from lexington.util import di
from lexington.util import route
from lexington.util import view_map
from lexington.util import paths

from lexington import exceptions

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
        self._dependencies.register_factory(
            'route_match',
            lambda routing, path, method: routing.path_to_route(path, method),
            ['routing', 'path', 'method']
        )
        self._dependencies.register_factory(
            'matched_route',
            lambda route_match: route_match[0],
            ['route_match'],
        )

        def current_view(view_map, matched_route):
            if matched_route is None:
                raise exceptions.NoRouteMatchedError()
            view = view_map.get_view(matched_route)
            if view is None:
                raise exceptions.NoViewForRouteError()
            return view

        self._dependencies.register_factory(
            'current_view',
            current_view,
            ['view_map', 'matched_route'],
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

        try:
            view = injector.get_dependency('current_view')
            result = injector.inject(view.fn, view.dependencies)
            if isinstance(result, Response):
                return result
            else: # Assume that the result is text
                return Response(result, mimetype='text/plain')
        except exceptions.NoRouteMatchedError:
            return self._404('Route not found')
        except exceptions.NoViewForRouteError:
            return self._404('No view found for route')

    def _404(self, message):
        return Response(message, status=404)
