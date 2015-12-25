from unittest import TestCase

from ..manager import BaseManager

manager = BaseManager()


class ManagerTest(TestCase):

    def setUp(self):
        self.manager = BaseManager()

    def test_register_unregister_simple(self):
        @self.manager.register('item')
        def somefunc(some, args):
            return sum(some, args)

        self.assertIn(somefunc.__name__, self.manager._registered['item'])
        self.assertIn(somefunc, self.manager._registered['item'].values())

        with self.assertRaises(ValueError):
            self.manager.register('item', item=somefunc)

        self.manager.unregister('item', somefunc)

        self.assertNotIn(somefunc.__name__, self.manager._registered['item'])
        self.assertNotIn(somefunc, self.manager._registered['item'].values())

    def test_register_unregister_custom_name(self):
        @self.manager.register('item', name='test')
        def somefunc(some, args):
            return sum(some, args)

        self.assertIn('test', self.manager._registered['item'])
        self.assertIn(somefunc, self.manager._registered['item'].values())

        self.manager.unregister('item', 'test')

        self.assertNotIn('test', self.manager._registered['item'])
        self.assertNotIn(somefunc, self.manager._registered['item'].values())

    def test_register_unregister_inner(self):
        @self.manager.register('item', related='asd')
        def somefunc(some, args):
            return sum(some, args)

        @self.manager.register('item', name='other', related='asd')
        def someotherfunc(some, args):
            return sum(some, args)

        self.assertIn(
            somefunc.__name__, self.manager._registered['item']['asd'])
        self.assertIn(
            somefunc, self.manager._registered['item']['asd'].values())

        self.assertIn('other', self.manager._registered['item']['asd'])
        self.assertIn(
            someotherfunc, self.manager._registered['item']['asd'].values())

        self.assertEqual(
            somefunc, self.manager.get('item', 'somefunc', related='asd'))
        self.assertEqual(
            someotherfunc, self.manager.get('item', 'other', related='asd'))

        self.manager.unregister('item', somefunc, related='asd')

        self.assertNotIn('test', self.manager._registered['item']['asd'])
        self.assertNotIn(
            somefunc, self.manager._registered['item']['asd'].values())

    def test_import_modules_register_no_decorator_and_overwrite(self):
        def old_request(data):
            return data * 4
        self.manager.register('request', item=old_request, name='handler')

        self.assertEqual(self.manager.get('request', 'handler')(4), 16)

        self.manager.import_modules(('mtr.utils.tests.testmodule:manager',))

        self.assertIn('item', self.manager._registered.keys())
        self.assertIn('request', self.manager._registered.keys())

        self.assertEqual(self.manager.get('request', 'handler')(4), 8)
        self.assertEqual(
            self.manager.get('item', 'some_item_func', related='asd')(2, 3, 4),
            sum((2, 3, 4)))

    def test_get_all_related_instances(self):
        @self.manager.register('nested', related='asd')
        def nested_one(data):
            return data * 4

        @self.manager.register('nested', related='bcd')
        def nested_two(data):
            return data * 5

        @self.manager.register('nested')
        def not_related_one(data):
            return data * 2

        @self.manager.register('nested')
        def not_related_two(data):
            return data

        for key, related in self.manager.all('nested').items():
            self.assertIn(key, (
                'asd', 'bcd', 'not_related_one', 'not_related_two'))

            if isinstance(related, dict):
                for rkey, value in related.items():
                    self.assertIn(rkey, ('nested_one', 'nested_two'))
                    self.assertIn(value, (nested_one, nested_two))
            else:
                self.assertIn(related, (not_related_one, not_related_two))
