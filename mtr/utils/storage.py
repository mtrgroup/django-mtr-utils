from django.core.files.storage import FileSystemStorage


class OverwriteDublicateFileSystemStorage(FileSystemStorage):

    def get_available_name(self, name):
        return name

    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super()._save(name, content)
