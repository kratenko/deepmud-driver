from collections import OrderedDict

class A(object):
    def __init__(self):
        print('init')

class Item(object):
    last_id = 0
    def __init__(self):
        last_id += 1
        self.id = 1
        self.environment = None


class Container(Item):
    def __init__(self):
        super().__init__()
        self.contents = OrderedDict()

    def insert(self, item):
        self.contents[item.id] = item
        item.environment = self

    def remove(self, item):
        item.environment = None
        del self.contents[item.id]

i1 = Item()
i2 = Item()

print(i1.id, i2.id)
