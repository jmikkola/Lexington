#!/usr/bin/env python3

import re
import unittest

# FIXME: this is using a relative import
import route

class PathSegmentTest(unittest.TestCase):
    def setUp(self):
        self._path_segment = route.PathSegment('/path-piece')

    def test_build_path(self):
        self.assertEqual('/path-piece', self._path_segment.build_path({}))

    def test_get_match(self):
        self.assertEqual('/path-piece', self._path_segment.get_match('/path-piece/x'))
        self.assertEqual(None, self._path_segment.get_match('/x/path-piece'))

    def test_get_name(self):
        self.assertEqual(None, self._path_segment.get_name())

class NamedPathSegmentTest(unittest.TestCase):
    def setUp(self):
        self._path_segment = route.NamedPathSegment('user_id', re.compile(r'\d+'))

    def test_no_pattern(self):
        path_segment = route.NamedPathSegment.no_pattern('name')
        self.assertEqual('Fry', path_segment.build_path({'name': 'Fry'}))
        self.assertEqual('Fry', path_segment.get_match('Fry/x/1'))
        self.assertEqual(None, path_segment.get_match('/Fry/'))

    def test_from_description(self):
        path1 = route.NamedPathSegment.from_description('user_id')
        self.assertEqual('user_id', path1.get_name())
        self.assertEqual('xyz', path1.get_match('xyz/123/'))

        path2 = route.NamedPathSegment.from_description('item_hash:\w+')
        self.assertEqual('item_hash', path2.get_name())
        self.assertEqual('a2dbd2', path2.get_match('a2dbd2/x'))
        self.assertEqual(None, path2.get_match('-x/x'))

    def test_build_path(self):
        # TODO: test case when value is missing and value doesn't match format
        self.assertEqual('1234', self._path_segment.build_path({'user_id': 1234}))

    def test_get_match(self):
        self.assertEqual('1234', self._path_segment.get_match('1234/xyz/'))
        self.assertEqual(None, self._path_segment.get_match('a1234/xyz/'))

    def test_get_name(self):
        self.assertEqual('user_id', self._path_segment.get_name())

class PathTest(unittest.TestCase):
    def setUp(self):
        self._path = route.Path([
            route.PathSegment('/users/'),
            route.NamedPathSegment('id', re.compile(r'\d+')),
            route.PathSegment('/'),
        ])

    def test_build_path(self):
        self.assertEqual('/users/1234/', self._path.build_path({'id': 1234}))

    def test_matches(self):
        self.assertEqual((True, {'id': '4567'}), self._path.matches('/users/4567/'))
        non_matches = ['/users/4567', 'users/4567/', 'x/users/4567/', '/users/4567/x']
        for path in non_matches:
            self.assertEqual((False, {}), self._path.matches(path))

    def test_from_description(self):
        path = route.Path.from_description('/user/{id:\d+}/')
        self.assertEqual('/user/1234/', path.build_path({'id': 1234}))
        self.assertEqual((True, {'id': '5678'}), path.matches('/user/5678/'))
        self.assertEqual((False, {}), path.matches('/user/xyz/'))

class RoutesTest(unittest.TestCase):
    def setUp(self):
        self._routes = route.Routes()

    def test_add_new_route(self):
        self._routes.add_route('user_page', 'GET', '/user/{id:\d+}/')

    def test_add_duplicate_route(self):
        pass # TODO: this

    def test_add_bad_route(self):
        pass # TODO: this

    def test_get_routing(self):
        self._routes.add_route('help', 'GET', '/help')
        self._routes.add_route('about', 'GET', '/about')
        routing = self._routes.get_routing()

        self.assertEqual({'help', 'about'}, set(routing.get_names()))

class RoutingTest(unittest.TestCase):
    def setUp(self):
        routes = route.Routes()
        routes.add_route('signup_page', 'GET', '/user/signup/')
        routes.add_route('user_page', 'GET', '/user/{id:\d+}/')
        routes.add_route('help', 'GET', '/help')
        routes.add_route('login_action', 'POST', '/login')
        self._routing = routes.get_routing()

    def test_get_names(self):
        self.assertEqual(
            {'signup_page', 'user_page', 'help', 'login_action'},
            set(self._routing.get_names())
        )

    def test_finds_routes(self):
        test_cases = [
            (('signup_page', {}), '/user/signup/', 'GET'),
            (('user_page', {'id': '12345'}), '/user/12345/', 'GET'),
            (('help', {}), '/help', 'GET'),
            (('login_action', {}), '/login', 'POST'),
            ((None, None), '/login', 'GET'),
            ((None, None), '/help', 'POST'),
            ((None, None), '/help/x/', 'GET'),
        ]
        for expected, path_string, method in test_cases:
            self.assertEqual(expected, self._routing.path_to_route(path_string, method))

    def test_builds_paths(self):
        pass

if __name__ == '__main__':
    unittest.main()
