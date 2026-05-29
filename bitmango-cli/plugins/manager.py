import os
import importlib.util
import inspect
import sys
from bitmango.plugins.base import BasePlugin
from bitmango.output import display_message
from bitmango.license import require_pro
from bitmango.messages import get_message

class PluginManager:
    def __init__(self, plugins_dir="plugins"):
        self.plugins_dir = plugins_dir
        self.plugins = []
        self._core_commands = [
            'entry', 'buy', 'sell', 'cancel', 'stop', 'exit', 'account', 'markets', 
            'history', 'leverage', 'margin', 'transfer', 'funding', 'funding-history',
            'position-mode', 'ledger', 'open_orders', 'query_order_book',
            'close', 'close-all', 'hello', 'ticker', 'ohlcv', 'trades',
            'order-status', 'closed-orders', 'deposits', 'withdrawals', 'position-risk'
        ]

    def load_plugin_for_command(self, command, subparsers, parent_parser):
        """
        Efficiently loads only the plugin that matches the requested command.
        """
        display_message('debug', get_message("plugins.debug_loading_command", command=command))
        if not command or command in self._core_commands:
            return False

        if not os.path.exists(self.plugins_dir):
            display_message('debug', get_message("plugins.debug_dir_not_found", dir=self.plugins_dir))
            return False

        # Normalize command name for matching files (e.g. trailing-stop -> trailing_stop)
        search_term = command.replace("-", "_")
        if search_term in ['trailing_stop', 'ghost_stop']:
            search_term = "smart_stops"
        elif search_term in ['iceberg', 'twap']:
            search_term = "pro_orders"
        
        display_message('debug', get_message("plugins.debug_searching_term", term=search_term, dir=self.plugins_dir))
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                if search_term in filename:
                    display_message('debug', get_message("plugins.debug_found_matching_file", filename=filename))
                    module_path = os.path.join(self.plugins_dir, filename)
                    if self._load_and_register(module_path, filename[:-3], subparsers, parent_parser):
                        return True
        return False

    def _load_and_register(self, module_path, module_name, subparsers, parent_parser):
        display_message('debug', get_message("plugins.debug_loading_module", module=module_name, path=module_path))
        
        try:
            # Ensure venv site-packages are in path if they exist
            venv_path = os.path.join(os.getcwd(), ".venv/lib/python3.11/site-packages")
            if os.path.exists(venv_path) and venv_path not in sys.path:
                sys.path.append(venv_path)

            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            module.__package__ = "plugins" 
            spec.loader.exec_module(module)
            
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    plugin_instance = obj()
                    display_message('debug', get_message("plugins.debug_loading_plugin", name=plugin_instance.name))
                    
                    # Wrap registration to inject a Pro check on the subparser's defaults
                    plugin_instance.register(subparsers, parent_parser)
                    
                    self.plugins.append(plugin_instance)
                    return True
        except Exception as e:
            display_message('error', get_message("plugins.error_loading_plugin", module=module_name, error=e))
            from bitmango.output import display_traceback
            display_traceback()
        return False

    def discover_and_load_all(self, subparsers, parent_parser):
        if not os.path.exists(self.plugins_dir):
            return

        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                self._load_and_register(os.path.join(self.plugins_dir, filename), filename[:-3], subparsers, parent_parser)

    def run_pre_command_hooks(self, args):
        """
        Runs the pre_command_check method on all loaded plugins.
        Also enforces Pro Tier for any command that is not a core command.
        """
        if args.command not in self._core_commands:
            require_pro(get_message("plugins.require_pro_msg", command=args.command))

        for plugin in self.plugins:
            # Skip Pro indicators if not actually requested for public commands
            if hasattr(plugin, 'name') and plugin.name == "Pro Technical Indicators":
                is_public = args.command in ['ohlcv', 'ticker', 'markets']
                has_indicators = getattr(args, 'rsi', None) or getattr(args, 'ema', None)
                if is_public and not has_indicators:
                    continue

            if hasattr(plugin, 'pre_command_check'):
                plugin.pre_command_check(args)

    def transform_result(self, result, args):
        """
        Allows plugins to modify the result object before final output.
        """
        transformed = result
        for plugin in self.plugins:
            # Skip Pro indicators if not actually requested for public commands
            if hasattr(plugin, 'name') and plugin.name == "Pro Technical Indicators":
                is_public = args.command in ['ohlcv', 'ticker', 'markets']
                has_indicators = getattr(args, 'rsi', None) or getattr(args, 'ema', None)
                if is_public and not has_indicators:
                    continue

            if hasattr(plugin, 'transform_result'):
                try:
                    transformed = plugin.transform_result(transformed, args)
                except Exception as e:
                    display_message('debug', get_message("plugins.debug_transform_failed", name=plugin.name, error=e))
        return transformed
