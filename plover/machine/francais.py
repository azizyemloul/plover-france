# Copyright (c) 2010 Joshua Harlan Lifton.
# See LICENSE.txt for details.

# TODO: add options to remap keys
# TODO: look into programmatically pasting into other applications

"For use with a Microsoft Sidewinder X4 keyboard used as stenotype machine."

# TODO: Change name to NKRO Keyboard.

# ABOUT francais.py:

# francais.py is not part of Plover. It's a try to mime the french
# Marc Grandjean Keyboard layout, a 21 keys keyboard.

# S P T * N   O A I n D
# K M F R L   E U l $ C
#           Y

# Plover can handle 24 keys. Then :

# S P T * N   O A I n D Z
# K M F R L   E U l $ C Q
#         L Y E

# The supplementary Z and Q and the doubled L and E keys are there to
# keep the integrity of the original sidewinder.py which is the
# template of this file. Thanks to the developpers.

# The supplementary L and E keys give a less stressing home position
# for thumbs and are welcome. Z and Q can give more extensibility to
# the originale method and they don't hurts further.

from plover.machine.base import StenotypeBase
from plover.oslayer import keyboardcontrol

KEYSTRING_TO_STENO_KEY = {"a": "K-",
                          "q": "S-",
                          "w": "P-",
                          "s": "M-",
                          "e": "T-",
                          "d": "F-",
                          "r": "*-",
                          "f": "R-",
                          "t": "N-",
                          "g": "L-",
                          "v": "L-",
                          "b": "Y-",
                          "y": "-O",
                          "h": "-E",
                          "n": "-E",
                          "u": "-A",
                          "j": "-U",
                          "i": "-I",
                          "k": "-l",
                          "o": "-n",
                          "l": "-$",
                          "p": "-D",
                          ";": "-C",
                          "[": "-Z",
                          "'": "-Q",
                          "1": "#",
                          "2": "#",
                          "3": "#",
                          "4": "#",
                          "5": "#",
                          "6": "#",
                          "7": "#",
                          "8": "#",
                          "9": "#",
                          "0": "#",
                          "-": "#",
                          "=": "#",
                         }


class Stenotype(StenotypeBase):
    """Standard stenotype interface for a Microsoft Sidewinder X4 keyboard.

    This class implements the three methods necessary for a standard
    stenotype interface: start_capture, stop_capture, and
    add_callback.

    """

    def __init__(self, params):
        """Monitor a Microsoft Sidewinder X4 keyboard via X events."""
        StenotypeBase.__init__(self)
        self._keyboard_emulation = keyboardcontrol.KeyboardEmulation()
        self._keyboard_capture = keyboardcontrol.KeyboardCapture()
        self._keyboard_capture.key_down = self._key_down
        self._keyboard_capture.key_up = self._key_up
        self.suppress_keyboard(True)
        self._down_keys = set()
        self._released_keys = set()
        self.arpeggiate = params['arpeggiate']

    def start_capture(self):
        """Begin listening for output from the stenotype machine."""
        self._keyboard_capture.start()
        self._ready()

    def stop_capture(self):
        """Stop listening for output from the stenotype machine."""
        self._keyboard_capture.cancel()
        self._stopped()

    def suppress_keyboard(self, suppress):
        self._is_keyboard_suppressed = suppress
        self._keyboard_capture.suppress_keyboard(suppress)

    def _key_down(self, event):
        """Called when a key is pressed."""
        if (self._is_keyboard_suppressed
            and event.keystring is not None
            and not self._keyboard_capture.is_keyboard_suppressed()):
            self._keyboard_emulation.send_backspaces(1)
        if event.keystring in KEYSTRING_TO_STENO_KEY:
            self._down_keys.add(event.keystring)

    def _post_suppress(self, suppress, steno_keys):
        """Backspace the last stroke since it matched a command.

        The suppress function is passed in to prevent threading issues with the
        gui.
        """
        n = len(steno_keys)
        if self.arpeggiate:
            n += 1
        suppress(n)

    def _key_up(self, event):
        """Called when a key is released."""
        if event.keystring in KEYSTRING_TO_STENO_KEY:
            # Process the newly released key.
            self._released_keys.add(event.keystring)
            # Remove invalid released keys.
            self._released_keys = self._released_keys.intersection(self._down_keys)

        # A stroke is complete if all pressed keys have been released.
        # If we are in arpeggiate mode then only send stroke when spacebar is pressed.
        send_strokes = bool(self._down_keys and
                            self._down_keys == self._released_keys)
        if self.arpeggiate:
            send_strokes &= event.keystring == ' '
        if send_strokes:
            steno_keys = [KEYSTRING_TO_STENO_KEY[k] for k in self._down_keys
                          if k in KEYSTRING_TO_STENO_KEY]
            if steno_keys:
                self._down_keys.clear()
                self._released_keys.clear()
                self._notify(steno_keys)

    @staticmethod
    def get_option_info():
        bool_converter = lambda s: s == 'True'
        return {
            'arpeggiate': (False, bool_converter),
        }
