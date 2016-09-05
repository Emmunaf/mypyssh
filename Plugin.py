import os
import sys
import importlib

'''
rcode
message
'''


class Plugin():
    """Class used to handle a (very) simple plugin system.

    """

    def __init__(self, path):
        """Initialize a Plugin class.

        Keyword arguments:
        path -- path of th plugins folder."""

        self.path = path
        self.commands_dict = {}
        # Add to sys_path the plugins dir
        sys.path.append(self.path)

    def _load_config(self):
        """Load config file and plugin."""

        if not os.path.exists("plugin.cfg"):
            raise IOError("No 'plugin.cfg' found!")
        with open("plugin.cfg") as f:
            for line in f.readlines()[2:]:  # The first 2 lines are skipped
                filename, classname = [x.strip() for x in line.split(":")]
                # Check if it is a valid plugin
                if os.path.exists('plugins/' + filename) and filename.endswith(".py"):
                    #print(filename, classname)
                    self.load(filename, classname)
                else:
                    print("!There was an issue loading the '%s' plugin [skipped]" % filename)

    def load(self, fname, cname):
        """Load a plugin, given its filename and classname"""

        mname, _ = os.path.splitext(fname)
        module = importlib.import_module(mname)
        globals()[cname] = module
        p = getattr(module, cname)()
        # TODO: Handle error, if get_commands ok
        # TODO: check if command is not already in the dict
        print(p.get_commands())
        # method is the name of the methode associated with the alias
        try:
            for alias, method in p.get_commands().items():
                self.commands_dict[alias] = {"classname": cname, "modulename": mname, "method": method}
        except Exception as e:
            del globals()[cname]
            print("Can't load the plugin: " + fname + "! [skipped]")

    def run(self, query):
        """Run a command of one loaded plugin."""

        # If there is a space char, split command from args
        if " " in query:
            cmd, cargs = query.split(" ", maxsplit=1)
        else:
            cmd = query
            cargs = None
        # Check if built-int help comand
        if cmd == 'help' or cmd == 'h':
            return self.doc(cargs)
        # Otherwise check for external plugin
        # Execute command if the command is in the commands dictionary
        if cmd not in self.commands_dict:
            print("There is no a such command.")  # Rprint
            return -1

        # Take the istance from global symbol table
        p = globals()[self.commands_dict[cmd]["classname"]]
        f = getattr(p, self.commands_dict[cmd]["classname"])()
        f2 = getattr(f, self.commands_dict[cmd]["method"])
        try:
            if cargs is not None:
                return f2(cargs)
            else:
                return f2()
        except:
            print("Can't run the plugin. Check the doc of your plugin. [help " + cmd + "]")  # Rprint
            return -1

    def doc(self, cmd):
        """Return the doc about a plugin (if any)

        Use python builtin __doc__ for help."""

        if cmd is None:
            print("Here there is a list of your installed plugin!")
            print("[Use help <plugin name> to read the doc about that plugin.]\n")
            # Show the list of all plugins
            for command in self.commands_dict.keys():
                print(command)
            return 0
        if cmd not in self.commands_dict:
            print("Can't show help information.\nNo such a plugin was found!")
            return -1
        p = globals()[self.commands_dict[cmd]["classname"]]
        f = getattr(p, self.commands_dict[cmd]["classname"])
        f2 = getattr(f, self.commands_dict[cmd]["method"])
        print(f2.__doc__)


'''p = globals()["plugin"]  # Take the istance from global symbol table
f = getattr(p, 'PluginClass"')
f()
f2 = getattr(f(), 'print_test')
f2()'''
test = Plugin("Plugins")
# test.load_all()
# test.run("printtest")
test._load_config()
while True:
    cmd = input("#-->")
    test.run(cmd)

# Nota: al metodo chiamato viene passato un unico argomento se la query aveva spazi:
# <cmd>[space]<args_of_method>
# Ex. help printtest
# Call help cmd with "printtest" args
# Every plugin needs a get_commands method used to retrieve the list of commands
# Every method in the plugin class NEED to return a dictionary
# Adding a plugin is easy as copying the plugin file to the Plugins folder and
#  add a new entry in plugin.cfg in the following format:
# <filenameofplugin.py> : <classname of plugin>
# The parser use : to split and ignore any space (You can use tab for formatting cfg file)
