import os
import importlib

# Default locale
DEFAULT_LOCALE = "en"

def get_message(key, **kwargs):
    """
    Retrieves a localized message by key and formats it with kwargs.
    Defaults to English if locale-specific message is not found.
    """
    locale = os.getenv("BITMANGO_LOCALE", DEFAULT_LOCALE)
    
    try:
        # Attempt to load the locale-specific module
        lang_mod = importlib.import_module(f"bitmango.messages.{locale}")
        messages = getattr(lang_mod, "MESSAGES", {})
    except (ImportError, AttributeError):
        # Fallback to English
        try:
            lang_mod = importlib.import_module(f"bitmango.messages.{DEFAULT_LOCALE}")
            messages = getattr(lang_mod, "MESSAGES", {})
        except:
            messages = {}

    msg_template = messages.get(key, f"Missing message key: {key}")
    
    try:
        return msg_template.format(**kwargs)
    except (KeyError, ValueError) as e:
        return f"Error formatting message '{key}': {e} (Template: {msg_template})"
