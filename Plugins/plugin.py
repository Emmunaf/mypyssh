class PluginClass:
    """Simple plugin class."""

    def __init__(self):

        self.commands = {"printtest": "print_test"}
        # print("Esempio")

    def print_test(self, msg):
        """Print example."""

        print("print_test %s" % msg)
        return {'rcode': 0,
                'message': "Message to print at the end"
                }

    def get_commands(self):
        return self.commands
