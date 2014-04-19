#!/usr/bin/env python3

import unittest

# FIXME: this is using a relative import
import di

class MissingDependenciesTest(unittest.TestCase):
    def _assert_result_for_graph_is(self, result, graph):
        dependency_graph = di.DependencyGraph(graph)
        self.assertEqual(result, dependency_graph.has_missing_dependencies())

    def _assert_missing_dependencies(self, graph):
        self._assert_result_for_graph_is(True, graph)

    def _assert_no_missing_dependencies(self, graph):
        self._assert_result_for_graph_is(False, graph)

    def test_approves_empty_graph(self):
        self._assert_no_missing_dependencies({})

    def test_approves_when_dependencies_met(self):
        self._assert_no_missing_dependencies({
            'a': ['b', 'c'],
            'b': ['c'],
            'c': [],
        })

    def test_rejects_when_missing_dependencies(self):
        self._assert_missing_dependencies({
            'a': ['b', 'c'],
            'b': ['c'],
        })

class CircularDependenciesTest(unittest.TestCase):
    def _assert_result_for_graph_is(self, result, graph):
        dependency_graph = di.DependencyGraph(graph)
        self.assertEqual(result, dependency_graph.has_circular_dependencies())

    def test_no_cycles_in_emtpy_graph(self):
        self._assert_result_for_graph_is(False, {})

    def test_no_cycles_in_good_graph(self):
        self._assert_result_for_graph_is(False, {
            'a': ['b', 'c'],
            'b': ['c'],
            'c': [],
        })

    def test_finds_cycles(self):
        self._assert_result_for_graph_is(True, {
            'a': ['b', 'c'],
            'b': ['c'],
            'c': ['d'],
            'd': ['b'],
        }
)
class DependenciesTest(unittest.TestCase):
    def setUp(self):
        self.dependencies = di.Dependencies()

    def test_can_add_things(self):
        self.dependencies.register_value('my value', 123)
        self.dependencies.register_factory('my factory', lambda: 1)
        self.dependencies.register_late_bound_value('late bound value')
        self.dependencies.register_dependant('dependant', di.Dependant(lambda: 1, []))

    def test_accepts_dependency_lists(self):
        self.dependencies.register_factory(
            'my factory', lambda: 1, dependencies=['my value']
        )

    def test_requires_names(self):
        with self.assertRaises(di.BadNameException):
            self.dependencies.register_value(None, 123)
        with self.assertRaises(di.BadNameException):
            self.dependencies.register_value(123, 123)
        with self.assertRaises(di.BadNameException):
            self.dependencies.register_value(object(), 123)

    def test_disallows_duplicate_names(self):
        self.dependencies.register_value('x', 1)
        with self.assertRaises(di.DuplicateNameException):
            self.dependencies.register_factory('x', lambda: 2)
        with self.assertRaises(di.DuplicateNameException):
            self.dependencies.register_late_bound_value('x')

        self.dependencies.register_late_bound_value('late')
        with self.assertRaises(di.DuplicateNameException):
            self.dependencies.register_value('late', 2)

    def test_lists_provided_dependencies(self):
        self.dependencies.register_value('x', 1)
        self.dependencies.register_factory('y', lambda: 2)
        self.dependencies.register_late_bound_value('z')
        self.assertEqual({'x', 'y', 'z'}, self.dependencies.provided_dependencies())

    def test_builds_injector(self):
        self.dependencies.register_value('x1', 1)
        self.dependencies.register_late_bound_value('late')
        inj = self.dependencies.build_injector(late_bound_values={
            'late': 123,
        })

        self.assertEqual(inj.get_dependency('x1'), 1)

    def test_can_depend_on_late_values(self):
        self.dependencies.register_factory(
            'args', lambda request: request['args'], dependencies=['request']
        )
        self.dependencies.register_late_bound_value('request')
        injector = self.dependencies.build_injector(late_bound_values={
            'request': {'args': 1234},
        })
        self.assertEqual(1234, injector.get_dependency('args'))

    def test_catches_missing_dependency(self):
        self.dependencies.register_factory('f1', lambda f2: 1, dependencies=['f2'])

        with self.assertRaises(di.MissingDependencyException):
            self.dependencies.build_injector()
        with self.assertRaises(di.MissingDependencyException):
            self.dependencies.check_dependencies()

    def test_catches_circular_dependency(self):
        self.dependencies.register_factory('f1', lambda f2: 1, dependencies=['f2'])
        self.dependencies.register_factory('f2', lambda f3: 2, dependencies=['f3'])
        self.dependencies.register_factory('f3', lambda f1: 3, dependencies=['f1'])

        with self.assertRaises(di.CircularDependencyException):
            self.dependencies.build_injector()
        with self.assertRaises(di.CircularDependencyException):
            self.dependencies.check_dependencies()

    def test_catches_missing_late_bound_value(self):
        self.dependencies.register_late_bound_value('val')
        with self.assertRaises(di.MissingDependencyException):
            self.dependencies.build_injector()

    def test_catches_unregistered_late_bound_value(self):
        with self.assertRaises(di.UnexpectedBindingException):
            self.dependencies.build_injector({
                'val': 1,
            })

class InjectorTest(unittest.TestCase):
    def setUp(self):
        self.injector = di.Injector({
            'value1': (lambda: 1, None),
            'value2': (lambda: 'some string', None),
            'factory1': (lambda: 'factory 1 result', None),
            'factory2': (lambda val1: 'value1 is {}'.format(val1), ['value1']),
        })

    def test_has_dependency(self):
        self.assertTrue(self.injector.has_dependency('value1'))
        self.assertFalse(self.injector.has_dependency('xyz'))

    def test_get_value(self):
        self.assertEqual(1, self.injector.get_dependency('value1'))
        self.assertEqual('some string', self.injector.get_dependency('value2'))

    def test_get_factory(self):
        self.assertEqual('factory 1 result', self.injector.get_dependency('factory1'))

    def test_get_factory_with_dependencies(self):
        self.assertEqual('value1 is 1', self.injector.get_dependency('factory2'))

    def test_inject(self):
        def test_fn(a, b):
            return '{} {}'.format(a, b)
        result = self.injector.inject(test_fn, ['value1', 'value2'])
        self.assertEqual('1 some string', result)

if __name__ == '__main__':
    unittest.main()
