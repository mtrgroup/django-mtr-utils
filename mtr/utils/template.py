from .manager import BaseManager
from .settings import SETTINGS


class ContextManager(BaseManager):
    pass


manager = ContextManager()
manager.import_modules(SETTINGS['template']['apps'])
