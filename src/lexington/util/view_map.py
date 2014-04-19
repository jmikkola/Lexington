"""
A mapping between routes and views
"""

import collections

class View(collections.namedtuple('View', 'fn route_name dependencies')):
    def __call__(self, *args):
        return self.fn(*args)

def view(route_name, dependencies):
    def view_wrapper(view_fn):
        return View(view_fn, route_name, dependencies)
    return view_wrapper

# FIXME: should inherit from base exception
class ViewMapException(Exception):
    pass

class ViewMapFactory:
    def __init__(self):
        self._route_to_view = dict()

    def add_view(self, view):
        route_name = view.route_name
        if route_name in self._route_to_view:
            raise ViewMapException('View already assigned for route {}'.format(route_name))
        self._route_to_view[route_name] = view

    def create(self, valid_route_names, provided_dependencies):
        for route_name, view in self._route_to_view.items():
            if route_name not in valid_route_names:
                raise ViewMapException('View mapped to nonexistant route {}'.format(route_name))
            for dependency in view.dependencies:
                if dependency not in provided_dependencies:
                    raise ViewMapException(
                        'View mapped to route depends on nonexistant dependency: {}'
                        .format(dependency)
                    )

        return ViewMap(self._route_to_view)

class ViewMap:
    def __init__(self, route_to_view):
        """ This class should be constructed using ViewMapFactory

        route_to_view - map from route name to view
        """
        self._route_to_view = route_to_view

    def get_view(self, route_name):
        """ Returns a view object, or None if no view matches the route name
        """
        return self._route_to_view.get(route_name)

    def get_routes(self):
        return self._route_to_view.keys()
