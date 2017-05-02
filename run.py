import logging

from cabinet import File, Cabinet

class World(object):
    def __init__(self):
        self.last_id = 0
        self.items = {}
        self.cabinet = Cabinet(root='cab')
    
    def next_id(self):
        self.last_id += 1
        return self.last_id
    
    

logging.basicConfig(level=logging.DEBUG)