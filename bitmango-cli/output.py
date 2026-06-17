import sys
import time
import threading
import os
import shutil
import logging
from logging.handlers import RotatingFileHandler

class Verbosity:
    DEFAULT = 0
    VERBOSE = 1
    DEBUG = 2

class OutputManager:
    """Handles standardized, colored, dynamic, and boxed output for the BitMango CLI."""
    
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = None
        self._current_text = ""
        self.use_colors = True
        self.boxed_mode = False
        self.json_mode = False
        self._box_width = 80 
        self.verbosity = Verbosity.DEFAULT
        self.last_error = None
        self.messages = [] # Accumulated messages for JSON mode
        
        # Initialize Persistent Logging
        self.logger = self._setup_file_logger()
        
        # ANSI Color Codes
        self.COLORS = {
            'blue': '\033[94m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'gray_dark': '\033[90m',
            'gray_light': '\033[37m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
        
        self.SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def _colorize(self, text, color):
        if not self.use_colors or self.json_mode:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['end']}"

    def strip_icons(self, text):
        """Removes emojis and special icons from text."""
        if not text or not isinstance(text, str):
            return text
        
        # Use a regex to strip common emoji ranges and specific icons used in the app
        import re
        # This regex covers most emojis and symbols used for flair
        # It targets the Unicode ranges for emojis, including skin tones and variants
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # flags (iOS)
            "\U00002702-\U000027b0"  # Dingbats
            "\U000024c2-\U0001f251"  # Enclosed Alphanumerics
            "\U0001f900-\U0001f9ff"  # Supplemental Symbols and Pictographs
            "\U0001fa70-\U0001faff"  # Symbols and Pictographs Extended-A
            "\U00002600-\U000026ff"  # Miscellaneous Symbols
            "\U00002300-\U000023ff"  # Miscellaneous Technical
            "\U00002190-\U000021ff"  # Arrows
            "\U00002b00-\U00002bff"  # Miscellaneous Symbols and Arrows
            "\U00002800-\U000028ff"  # Braille Patterns (Spinners)
            "\ufe00-\ufe0f"          # Variation selectors
            "]+", flags=re.UNICODE
        )
        
        # Also handle variation selectors and specific multi-byte characters if needed
        text = emoji_pattern.sub('', text)
        
        # Clean up any resulting double spaces or trailing whitespace
        return text.replace('  ', ' ').strip()

    def _setup_file_logger(self):
        """Sets up an append-only file logger."""
        try:
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_file = os.path.join(log_dir, "bitmango.log")
            
            logger = logging.getLogger("bitmango")
            logger.setLevel(logging.DEBUG)
            
            # Use RotatingFileHandler to prevent log file from growing indefinitely
            # 5MB per file, keep 5 backups
            handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            
            if not logger.handlers:
                logger.addHandler(handler)
            
            return logger
        except Exception as e:
            # Fallback if logging setup fails (e.g. permission issues)
            # Use sys.stderr to avoid polluting JSON output
            print(f"Warning: Could not initialize file logging: {e}", file=sys.stderr)
            return logging.getLogger("null")

    def start_boxed_mode(self, title="TRADING OPERATION"):
        """Draws the top of a single-line gray box."""
        if self.boxed_mode or self.json_mode:
            return
        self.boxed_mode = True
        self._box_width = self._get_terminal_width() - 2
        
        top_border = "┌" + "─" * (self._box_width) + "┐"
        print(self._colorize(top_border, 'gray_dark'))
        
        padding = (self._box_width - len(title)) // 2
        title_line = "│" + " " * padding + title + " " * (self._box_width - len(title) - padding) + "│"
        print(self._colorize(title_line, 'gray_dark'))
        
        mid_border = "├" + "─" * (self._box_width) + "┤"
        print(self._colorize(mid_border, 'gray_dark'))
        sys.stdout.flush()

    def stop_boxed_mode(self):
        """Draws the bottom of a single-line gray box."""
        if not self.boxed_mode or self.json_mode:
            return
        bottom_border = "└" + "─" * (self._box_width) + "┘"
        print(self._colorize(bottom_border, 'gray_dark'))
        self.boxed_mode = False
        sys.stdout.flush()

    def _get_terminal_width(self):
        try:
            # Prefer a standard width for consistency, but shrink if terminal is smaller
            # Capping at 80 makes it readable even on large terminals without being too wide.
            columns = shutil.get_terminal_size((80, 20)).columns
            return min(columns, 80)
        except:
            return 80

    def _format_line(self, text, color_key='end'):
        """Wraps text in single-line gray side borders if in boxed mode."""
        if not self.boxed_mode or self.json_mode:
            return self._colorize(text, color_key)
        
        # Indent inside box
        content = "  " + text
        padding = self._box_width - len(content)
        if padding < 0: # Handle overflow
            content = content[:self._box_width-3] + "..."
            padding = 0
            
        left = self._colorize("│", "gray_dark")
        right = self._colorize("│", "gray_dark")
        return f"{left}{self._colorize(content + ' ' * padding, color_key)}{right}"

    def render_result(self, result):
        """Final output rendering. Proxies to bitmango.cli.renderer."""
        from bitmango.cli.renderer import render_result as internal_renderer
        return internal_renderer(self, result)

    def print_message(self, m_type, text, icon=None):
        """Standard colored print. Respected verbosity and new color rules."""
        if m_type == 'error':
            self.last_error = text

        # Persistent Logging (Always append-only to file)
        log_level = logging.INFO
        if m_type == 'debug': log_level = logging.DEBUG
        elif m_type == 'warning': log_level = logging.WARNING
        elif m_type == 'error': log_level = logging.ERROR
        elif m_type == 'success': log_level = logging.INFO
        
        self.logger.log(log_level, text)

        if self.json_mode:
            # In JSON mode, we accumulate all human-readable messages
            # so they can be optionally included in the final JSON object.
            # We strip icons from JSON logs to keep them machine-friendly.
            clean_text = self.strip_icons(text)
            self.messages.append({"level": m_type, "message": clean_text})
            return

        if m_type == 'info' and self.verbosity < Verbosity.DEFAULT:
            return
        if m_type == 'debug' and self.verbosity < Verbosity.DEBUG:
            return

        text_color = 'gray_light'
        icon_color = 'end'
        default_icon = ""
        
        if m_type == 'success':
            text_color = 'gray_light'
            icon_color = 'green'
            default_icon = "✓"
        elif m_type == 'info':
            text_color = 'gray_light'
            default_icon = ""
        elif m_type == 'warning':
            # Severe warning -> full color
            text_color = 'yellow'
            icon_color = 'yellow'
            default_icon = "⚠️"
        elif m_type == 'error':
            # Extreme case -> full color
            text_color = 'red'
            icon_color = 'red'
            default_icon = "❌"
        elif m_type == 'debug':
            text_color = 'gray_dark' # Inactive/Background
            default_icon = ""
            
        final_icon = icon if icon else default_icon
        
        # Construct line: [Colored Text] [Colored Icon]
        colored_text = self._colorize(text, text_color)
        colored_icon = self._colorize(final_icon, icon_color) if final_icon else ""
        
        msg = f"{text} {final_icon}".strip()
        # Note: _format_line handles the overall coloring if not boxed
        # But we want internal coloring. 
        # Actually _format_line takes a color_key for the WHOLE line.
        # We need to change _format_line to accept pre-colored text.
        
        full_msg = f"{colored_text} {colored_icon}".strip()
        print(self._format_line_precolored(full_msg))
        sys.stdout.flush()

    def _wrap_text(self, text, max_width):
        """Wraps text into multiple lines, preserving ANSI codes."""
        import re
        ansi_escape = re.compile(r'(\x1B(?:[@-Z\\-_]|\[[0-?]* [ -/]*[@-~]))')
        
        # Split text into parts (text and ANSI codes)
        parts = ansi_escape.split(text)
        
        wrapped_lines = []
        current_line = ""
        current_line_width = 0
        active_ansi_codes = []
        
        for part in parts:
            if ansi_escape.match(part):
                current_line += part
                # Keep track of active ANSI codes to re-apply them on new lines
                if part == '\033[0m':
                    active_ansi_codes = []
                else:
                    active_ansi_codes.append(part)
            else:
                # Actual text content
                words = part.split(' ')
                for i, word in enumerate(words):
                    # Add space if not first word
                    word_to_add = word + (" " if i < len(words) - 1 else "")
                    word_width = len(word_to_add) # Basic len for now, wcwidth is better but complex with parts
                    
                    if current_line_width + word_width > max_width:
                        # Close current line
                        # Strip trailing space before closing
                        current_line = current_line.rstrip()
                        if active_ansi_codes:
                            current_line += '\033[0m'
                        wrapped_lines.append(current_line)
                        
                        # Start new line
                        current_line = "".join(active_ansi_codes) + word_to_add
                        current_line_width = word_width
                    else:
                        current_line += word_to_add
                        current_line_width += word_width
        
        if current_line:
            wrapped_lines.append(current_line.rstrip())
            
        return wrapped_lines

    def _format_line_precolored(self, colored_text, end_line=True):
        """Version of format line that assumes text is already ANSI colored."""
        if self.json_mode:
            return colored_text

        if not self.boxed_mode:
            return colored_text
        
        import re
        from wcwidth import wcswidth
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        # Calculate width of plain text
        plain_text = ansi_escape.sub('', colored_text)
        visible_width = wcswidth(plain_text)
        if visible_width == -1:
            visible_width = len(plain_text)
            
        max_content_width = self._box_width - 4
        
        # If it fits, return single line
        if visible_width <= max_content_width:
            content = "  " + colored_text
            if not end_line:
                left = self._colorize("│", "gray_dark")
                return f"\033[K{left}{content}"

            padding_len = max_content_width - visible_width
            padding = " " * padding_len
            left = self._colorize("│", "gray_dark")
            right = self._colorize("│", "gray_dark")
            return f"\033[K{left}{content}{padding}  {right}"
        
        # Otherwise, wrap
        wrapped = self._wrap_text(colored_text, max_content_width)
        formatted_lines = []
        
        for i, line in enumerate(wrapped):
            # Calculate visible width of this chunk
            p_line = ansi_escape.sub('', line)
            v_width = wcswidth(p_line)
            if v_width == -1: v_width = len(p_line)
            
            content = "  " + line
            padding_len = max_content_width - v_width
            padding = " " * padding_len
            
            left = self._colorize("│", "gray_dark")
            right = self._colorize("│", "gray_dark")
            
            formatted_lines.append(f"\033[K{left}{content}{padding}  {right}")
            
        return "\n".join(formatted_lines)

    def start_action(self, text):
        """Starts a dynamic spinner on a single line."""
        if self.json_mode:
            return
        # Defensive: Stop existing action if running
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()
            
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._animate, args=(text,))
        self._thread.start()

    def stop_action(self, final_text=None, result_icon="✓", m_type='success'):
        """Stops the spinner and shows the result."""
        if self.json_mode:
            return
        if self._thread:
            self._stop_event.set()
            self._thread.join()
            
            text_to_show = final_text if final_text else self._current_text
            
            text_color = 'gray_light'
            icon_color = 'green'
            
            if m_type == 'error':
                text_color = 'red'
                icon_color = 'red'
            elif m_type == 'warning':
                text_color = 'yellow'
                icon_color = 'yellow'
            elif m_type == 'info':
                text_color = 'gray_light'
                icon_color = 'end'
            
            colored_text = self._colorize(text_to_show, text_color)
            colored_icon = self._colorize(result_icon, icon_color)
            
            full_msg = f"{colored_text} {colored_icon}".strip()
            line = self._format_line_precolored(full_msg)
            
            # Write final line and newline
            sys.stdout.write(f"\r{line}\n")
            sys.stdout.flush()
            self._thread = None

    def _animate(self, text):
        self._current_text = text
        frame_idx = 0
        while not self._stop_event.is_set():
            frame = self.SPINNER_FRAMES[frame_idx % len(self.SPINNER_FRAMES)]
            colored_text = self._colorize(text, 'gray_light')
            colored_frame = self._colorize(frame, 'blue')
            content = f"{colored_text} {colored_frame}"
            
            # Use carriage return and clear to end of line before printing
            line = self._format_line_precolored(content)
            sys.stdout.write(f"\r{line}")
            sys.stdout.flush()
            frame_idx += 1
            time.sleep(0.1)

    def prompt_user(self, text, mask=False):
        """Prompts the user for input while maintaining boxed UI borders."""
        if self.json_mode:
            return "" # Should not happen in JSON mode as we auto-confirm
            
        import getpass
        
        colored_prompt = self._colorize(text, 'gray_light')
        line = self._format_line_precolored(colored_prompt, end_line=False)
        
        sys.stdout.write(f"\r{line}")
        sys.stdout.flush()
        
        if mask:
            user_input = getpass.getpass("")
        else:
            user_input = input("")
            
        # After input, we need to "close" the line by printing the right border
        # Professional way: rewrite the line with the input (redacted if mask)
        display_val = "********" if mask else user_input
        full_line_text = f"{text}{display_val}"
        # Print one line up to replace the user's raw input with a formatted boxed line
        sys.stdout.write("\033[A\r")
        print(self._format_line_precolored(self._colorize(full_line_text, 'gray_light')))
        
        return user_input

# Singleton instance
output = OutputManager()

def display_message(m_type, text, icon=None, result_icon=None):
    if m_type in ['success', 'info', 'warning', 'error', 'debug']:
        output.print_message(m_type, text, icon)
    elif m_type == 'loading' or m_type == 'action_start':
        output.start_action(text)
    elif m_type == 'action_stop':
        res_type = 'success'
        r_icon = result_icon or "✓"
        if r_icon in ["❌", "🛑"]:
            res_type = 'error'
        elif r_icon in ["⚠️", "⏳"]:
            res_type = 'warning'
        output.stop_action(text, r_icon, m_type=res_type)

def display_traceback():
    """Captures and displays the current exception traceback inside the boxed UI."""
    import traceback
    tb_text = traceback.format_exc()
    output.logger.error(f"Traceback captured:\n{tb_text}")
    
    tb_lines = tb_text.splitlines()
    for line in tb_lines:
        display_message('error', f"  {line}")

def start_boxed_mode(title="TRADING OPERATION"):
    output.start_boxed_mode(title)

def stop_boxed_mode():
    output.stop_boxed_mode()

def prompt_user(text, mask=False):
    return output.prompt_user(text, mask)
