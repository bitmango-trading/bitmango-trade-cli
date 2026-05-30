import abc

class BasePlugin(abc.ABC):
    """
    Base class for all BitMango plugins.
    """
    
    @property
    @abc.abstractmethod
    def name(self):
        """The name of the plugin."""
        pass

    @property
    @abc.abstractmethod
    def description(self):
        """A brief description of the plugin's functionality."""
        pass

    @abc.abstractmethod
    def register(self, subparsers, parent_parser):
        """
        Hook to register new commands/subparsers into the main bitmango CLI.
        """
        pass
