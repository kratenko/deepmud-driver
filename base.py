
class Item(object):
    def __init__(self):
        self.environment = None

    def can_enter(self, item):
        return False

class Container(Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contents = []

    def can_enter(self, item):
        return True

    def insert(self, item):
        self.contents.append(item)
        item.environment = self

    def remove(self, item):
        self.contetns.remove(item)
        item.environment = None
