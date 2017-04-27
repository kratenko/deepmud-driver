import logging
import yaml
import lupa

class Item(object):
    pass


class InheritanceException(Exception):
    pass


class Lu(object):
    def __init__(self):
        self.lua = lupa.LuaRuntime()
    
    def eval(self, *args, **kwargs):
        return self.lua.eval(*args, **kwargs)


class Blueprint(object):
    def __init__(self, table, path):
        self.table = table
        self.path = path
        self.extention = '.yaml'
        self.full_path = self.path + self.extention
        # TODO: chance ancestors to be an ordered set
        self.ancestors = []
        #
        self.name = None
        self.short = None
        self.long = None
        self.variables = {}
        self.functions = {}
        self.load()

    def load(self):
        if self.path.startswith('/base/'):
            self.is_base = True
            y = self._load_base()
        else:
            self.is_base = False
            with open(self.full_path) as f:
                y = yaml.load(f)
        print(y)
        if 'inherit' in y:
            self._inheritance(y['inherit'])
        if 'name' in y:
            self.name = y['name'].strip()
        if 'short' in y:
            self.short = y['short'].strip()
        if 'long' in y:
            self.long = y['long'].strip()
        if 'functions' in y:
            self._compile(y['functions'])
        self.definition = y

    def _compile(self, fdefs):
        for fname, fdef in fdefs.items():
            fun = self.table.lu.eval(fdef)
            self.functions[fname] = fun
            

    def _inheritance(self, inherit):
        if type(inherit) is str:
            inherit = [inherit]
        for i_path in inherit:
            # no self inheritance
            if i_path == self.path:
                raise InheritanceException("'%s' tried to inherit from itself" % self.path)
            # no multiple inheritance of one blueprint
            if i_path in self.ancestors:
                raise InheritanceException("Double inheritance of '%s'" % i_path)
            i = self.table.get_blueprint(i_path)
            # no loops:
            if self.path in i.ancestors:
                raise InheritanceException("Circular inheritance")
            # check for collisions of inheritance with ancestor
            if set(self.ancestors).intersection(i.ancestors):
                raise InheritanceException("%s cannot inherit from %s, common ancestors exist" % (self.path, i_path))
            # seems fine, inherit:
            if i.name is not None:
                self.name = i.name
            if i.short is not None:
                self.short = i.short
            if i.long is not None:
                self.long = i.long
            self.ancestors.append(i_path)

    def create(self):
        i = Item()
        i.blueprint = self
        i.name = self.name
        i.short = self.short
        i.long = self.long
        if 'create' in self.functions:
            self.functions['create'](i)
        return i

    def _load_base(self):
        if self.path == '/base/room':
            return {}
        else:
            raise KeyError("Invalid base blueprint: '%s'" % self.path)


class BlueprintTable(object):
    def __init__(self, lu):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Setting up blueprint table")
        self.lu = lu
        self.store = {}

    def get_blueprint(self, path):
        if path in self.store:
            return self.store[path]
        else:
            return self._load_blueprint(path)
    
    def _load_blueprint(self, path):
        self.logger.info("Loading blueprint: '%s'", path)
        bp = Blueprint(self, path)
        self.store[path] = bp
        return bp


logging.basicConfig(level=logging.DEBUG)

lu = Lu()
bpt = BlueprintTable(lu)
r1 = bpt.get_blueprint('rooms/r1')

i = r1.create()
print(i.long)
print(i.blueprint.ancestors)

