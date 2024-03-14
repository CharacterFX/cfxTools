'''
A Class for reloading modules in python 2 or 3
Author: John Riggs

'''
import platform

class moduleTools(object):

    def __init__(self):
        self.pythonVer = int(platform.python_version().split(".")[0])

    def reload(self, modules):

        '''
        This bypasses the need to do this in every script that needs to have modules reloaded
        @param modules:
            the modules to reload
        '''

        if not isinstance(modules, list):
            modules = [modules]
            
        for md in modules:
            print('Reloading Module: ', md)
            if self.pythonVer > 2:
                import importlib
                importlib.reload(md)
            else:
                importlib.reload(md)