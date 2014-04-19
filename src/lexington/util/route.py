import re
import collections

NO_SLASH_PATTERN = re.compile(r'[^/]+')

Route = collections.namedtuple('Route', 'name path method')

class PathSegment:
    def __init__(self, path):
        self._path = path

    def build_path(self, values):
        return self._path

    def get_match(self, text):
        if text.startswith(self._path):
            return self._path
        return None

    def get_name(self):
        return None

class NamedPathSegment(PathSegment):
    def __init__(self, name, pattern):
        self._name = name
        self._pattern = pattern

    @classmethod
    def no_pattern(cls, name):
        return cls(name, NO_SLASH_PATTERN)

    @classmethod
    def from_description(cls, description):
        name, _, regex = description.partition(':')
        if regex:
            return cls(name, re.compile(regex))
        else:
            return cls.no_pattern(name)

    def build_path(self, values):
        if self._name not in values:
            pass # TODO: throw an exception
        value = str(values[self._name])
        if self.get_match(value) is None:
            pass # TODO: throw an exception
        return value

    def get_match(self, text):
        match = self._pattern.match(text)
        if match:
            return match.group()
        return None

    def get_name(self):
        return self._name

SEGMENT_RE = re.compile(r'^([^{}]+|\{[^{}]+\})')

class Path:
    def __init__(self, segments):
        self._segments = segments

    @classmethod
    def from_description(cls, description):
        # TODO: for now, assuming that pattern has no braces
        segments = []
        while description:
            match = SEGMENT_RE.match(description)
            if not match:
                raise Exception("TODO: this")
            segment_text = match.group()
            description = description[len(segment_text):]

            if segment_text.startswith('{'):
                segment = NamedPathSegment.from_description(segment_text[1:-1])
            else:
                segment = PathSegment(segment_text)
            segments.append(segment)
        return cls(segments)

    def build_path(self, values):
        return ''.join(segment.build_path(values) for segment in self._segments)

    def matches(self, path):
        matched_values = {}
        path_tail = path
        for segment in self._segments:
            match = segment.get_match(path_tail)
            if match:
                path_tail = path_tail[len(match):]
                if segment.get_name():
                    matched_values[segment.get_name()] = match
            else:
                return (False, {})
        if len(path_tail) > 0:
            return (False, {})
        return (True, matched_values)

class Routes:
    def __init__(self):
        self._routes = []
        self._names = set()

    def add_route(self, name, method, path_description):
        if name in self._names:
            raise Exception('duplicate route name: {}'.format(name)) # TODO: clean up name
        # TODO: raise an exception if name, path, or method is not valid
        path = Path.from_description(path_description)
        self._routes.append(Route(name, path, method))
        self._names.add(name)

    def get_routing(self):
        return Routing([route for route in self._routes])

class Routing:
    def __init__(self, routes):
        self._routes = routes
        self._routes_by_name = {
            route.name: route
            for route in self._routes
        }

    def get_names(self):
        return self._routes_by_name.keys()

    def path_to_route(self, path_string, method):
        for (name, path, route_method) in self._routes:
            if method == route_method:
                matches, values = path.matches(path_string)
                if matches:
                    return name, values
        return None, None

    def route_to_path(self, route_name, values):
        # TODO: throw an exception if route_name is not in
        return self._routes_by_name[route_name].path.build_path(values)
