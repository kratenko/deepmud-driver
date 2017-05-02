import os
import logging

import yaml
import lupa


logger = logging.getLogger(__name__)

class InheritanceException(Exception):
    pass

class File(object):
    def __init__(self, cabinet, path):
        self.cabinet = cabinet
        self.path = path
        self.inherit = None
        self.inherited = []
        self.descriptive = None
        self.function_definitions = None
        self.functions = {}

    def load(self):
        #full_path = os.path.join(self.cabinet.root, self.path)
        if self.path.startswith('/'):
            path = self.path[1:]
        else:
            path = self.path
        full_path = os.path.join(self.cabinet.root, path)
        yaml_path = full_path + '.yaml'
        with open(yaml_path, "rt") as f:
            y = yaml.load(f)
        # store inheritance definition, make sure it is a list:
        if 'inherit' in y:
            if type(y['inherit']) is list:
                self.inherit = y['inherit']
            else:
                self.inherit = [y['inherit']]
        # store the descriptive part:
        if 'descriptive' in y:
            self.descriptive = y['descriptive']
        # store executable part, for compilation:
        if 'functions' in y:
            self.function_definitions = y['functions']

    def inheritance(self):
        print(self.inherit)
        if self.inherit:
            for i in self.inherit:
                self.inheritance_one(i)

    def inheritance_one(self, i_path):
        if i_path == self.path:
            raise InheritanceException("Tried to inherit self")
        if i_path in self.inherited:
            raise InheritanceException("Tried to inherit '%s' twice" % i_path)
        i = self.cabinet.get_compiled_file(i_path)
        shared = set(self.inherited).intersection(i.inherited)
        if shared:
            raise InheritanceException(
                "Cannot inherit '%s', common ancestors: %s" %(i, shared))
        self.inherited.extend(i.inherited)
        self.inherited.append(i_path)


    def compile(self):
        self.inheritance()
        logger.info("compiling '%s'", self.path)
        if self.function_definitions:
            for f_name, f_def in self.function_definitions.items():
                fun = self.cabinet.eval(f_def)
                self.functions[f_name] = fun


class Cabinet(object):
    def __init__(self, root):
        logger.info("Setting up file cabinet with root '%s'", root)
        self.root = root
        self.files = {}
        logger.info("Setting up lua runtime environment")
        self.lua = lupa.LuaRuntime(  # @UndefinedVariable
            register_eval=False,
            unpack_returned_tuples=True,
        )

    def eval(self, *args, **kwargs):
        return self.lua.eval(*args, **kwargs)

    def load_file(self, path):
        logger.info("Loading file '%s'", path)
        f = File(self, path)
        f.load()
        f.compile()
        self.files[path] = f
        return f

    def get_compiled_file(self, path):
        if path in self.files:
            return self.files[path]
        else:
            return self.load_file(path)


#logging.basicConfig(level=logging.DEBUG)
#cab = Cabinet('cab')
#r1 = cab.get_compiled_file('rooms/r1')
#print(r1.functions)
#r1.functions['create']()
