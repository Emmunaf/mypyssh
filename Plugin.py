import os
import sys
import importlib


class Plugin():
    """Class used to handle a basic plugin system.

    """

    def __init__(self, path):
        """Path is the directory where plugins are stored.
        """
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
                if os.path.exists('plugins/'+filename) and filename.endswith(".py"):
                    print(filename, classname)
                    self.load(filename, classname)
                else:
                    print("!There was an issue loading the '%s' plugin [skipped]" % filename)

    def load(self, fname, cname):
        """Load a plugin, given its filename and classname"""

        name, _ = os.path.splitext(fname)
        module = importlib.import_module(name)
        globals()[cname] = module
        p = getattr(module, cname)()
        # TODO: Handle error, if get_commands ok
        # TODO: check if command is not already in the dict
        self.commands_dict[name] = {"classname" : cname, "commands" : p.get_commands()}


    def run(self, query):
        """Run a command of the loaded plugins."""

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
        for plugin in self.commands_dict:
            if cmd in self.commands_dict[plugin]["commands"]:
                # Execute command
                # Take the istance from global symbol table
                p = globals()[self.commands_dict[plugin]["classname"]] 
                f = getattr(p, self.commands_dict[plugin]["classname"])()
                f2 = getattr(f, self.commands_dict[plugin]["commands"][cmd])
                try:
                    if cargs is not None:
                        return f2(cargs)
                    else:
                        return f2()
                except:
                    print("Can't run the plugin. Check your plugin.")  # Rprint
                    return -1
        print("No such command was found")  # Rprint

    def doc(self, cmd):
        """Return the doc about a plugin (if any)

        Use python builtin __doc__ for help."""

        for plugin in self.commands_dict:
            if cmd in self.commands_dict[plugin]["commands"]:
                # Execute command
                p = globals()[self.commands_dict[plugin]["classname"]]
                f = getattr(p, self.commands_dict[plugin]["classname"])()
                f2 = getattr(f, self.commands_dict[plugin]["commands"][cmd])
                print(f2.__doc__)  # Rprint
            else:
                print("Can't show help information.\nNo such plugin was found!")  # RPrint

# ex = plugin.PluginClass"()
'''p = globals()["plugin"]  # Take the istance from global symbol table
f = getattr(p, 'PluginClass"')
f()
f2 = getattr(f(), 'print_test')
f2()'''
test = Plugin("Plugins")
#test.load_all()
test.run("printtest")
test._load_config()
while True:
    cmd = input("#-->")
    test.run(cmd)

#Nota: al metodo chiamato viene passato un unico argomento se la query aveva spazi:
#<cmd>[space]<args_of_method>
# Ex. help printtest
# Call help cmd with "printtest" args
# Every plugin needs a get_commands method used to retrieve the list of commands
# Every method in the plugin class NEED to return a dictionary
# Adding a plugin is easy as copying the plugin file to the Plugins folder and
#  add a new entry in plugin.cfg in the following format:
#<filenameofplugin.py> : <classname of plugin>
# The parser use : to split and ignore any space (You can use tab for formatting cfg file)

