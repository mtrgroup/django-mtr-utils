from .manager import manager


@manager.register('item', related='asd')
def some_item_func(*args):
    return sum(args)


@manager.register('request')
def handler(data):
    return data * 2
