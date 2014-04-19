#!/usr/bin/env python

# FIXME: use absolute import
import view_map

import unittest

def _view(name, *dependencies):
    return view_map.View(lambda: None, name, dependencies)

class ViewMapFactoryTest(unittest.TestCase):
    def setUp(self):
        self._vmf = view_map.ViewMapFactory()

    def test_adds_view(self):
        self._vmf.add_view(_view('index'))

    def test_enforces_single_assignment(self):
        self._vmf.add_view(_view('hello'))
        with self.assertRaises(view_map.ViewMapException):
            self._vmf.add_view(_view('hello'))

    def test_builds_view_map(self):
        self._vmf.add_view(_view('hello', 'dep1'))
        result = self._vmf.create(['hello', 'index'], {'dep1'})
        self.assertTrue(bool(result))

    def test_requires_route_to_exist(self):
        self._vmf.add_view(_view('hello'))
        with self.assertRaises(view_map.ViewMapException):
            self._vmf.create(['index'], set())

    def test_requires_dependency_to_exist(self):
        self._vmf.add_view(_view('hello', 'dep1'))
        with self.assertRaises(view_map.ViewMapException):
            self._vmf.create(['hello'], set())

class ViewMapTest(unittest.TestCase):
    def setUp(self):
        self._vm = view_map.ViewMap({
            'hello': 1,
            'index': 2,
            'help': 3,
        })

    def test_get_view(self):
        self.assertEqual(3, self._vm.get_view('help'))

    def test_route_list(self):
        self.assertEqual({'hello', 'index', 'help'}, self._vm.get_routes())

if __name__ == '__main__':
    unittest.main()
