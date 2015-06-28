import json
import sys
import shutil
import os

class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


@Singleton
class Config:

    def __init__(self):
        with open( '../cacheImagery/config.json') as config_file:
            self.data = json.load(config_file )
            self.tmpdir = []

    #Main accessor for configuration data
    def getConfig(self):
        return self.data

    #Return the config file path, creating it if necessary
    def getTempDir(self):
        if not self.tmpdir:
            self.tmpdir = Config.Instance().getConfig()['detecting']['tmpDirectory'] + '/'
            if not os.path.isdir( self.tmpdir ):
                # Let the exception be thrown if it fails
                os.makedirs( self.tmpdir)

        return self.tmpdir

    #Remove anything created by this config file (e.g., temp directory)
    def cleanup(self):
        if self.tmpdir:
            shutil.rmtree( self.tmpdir )
            self.tmpdir = []

    def inDebugMode(self):
        inDebug = False
        if sys.gettrace():
            inDebug = True

        return inDebug


