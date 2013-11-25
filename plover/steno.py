# Copyright (c) 2010-2011 Joshua Harlan Lifton.
# See LICENSE.txt for details.

# TODO: unit test this file

# PLOVER-FRANCE Modifications:
# ----------------------------
# This file is a modified version of the original steno.py. Trying to
# handle the Marc Grandjean french layout.
#
# IMPLICIT_HYPHENS and IMPLICIT_HYPHEN are set to the key 'Y'.
#
# The CORRECTION STROKE in french stenography is "-Ul$C", the
# four right fingers pressing all together on the home position.

"""Generic stenography data models.

This module contains the following class:

Stroke -- A data model class that encapsulates a sequence of steno keys.

"""

import re

STROKE_DELIMITER = '/'
IMPLICIT_HYPHENS = set('Y')

def normalize_steno(strokes_string):
    """Convert steno strings to one common form."""
    strokes = strokes_string.split(STROKE_DELIMITER)
    normalized_strokes = []
    for stroke in strokes:
        if '#' in stroke:
            stroke = stroke.replace('#', '')
            if not re.search('[0-9]', stroke):
                stroke = '#' + stroke
        has_implicit_dash = bool(set(stroke) & IMPLICIT_HYPHENS)
        if has_implicit_dash:
            stroke = stroke.replace('-', '')
        if stroke.endswith('-'):
            stroke = stroke[:-1]
        normalized_strokes.append(stroke)
    return tuple(normalized_strokes)

STENO_KEY_NUMBERS = {'S-': '1-',
                     'P-': '2-',
                     'T-': '3-',
                     '*-': '4-',
                     'N-': '5-',
                     'Y-': '0-',
                     '-O': '-6',
                     '-A': '-7',
                     '-I': '-8',
                     '-ᴎ': '-9'}

STENO_KEY_ORDER = {"S-": 0,
                   "K-": 1,
                   "P-": 2,
                   "M-": 3,
                   "T-": 4,
                   "F-": 5,
                   "*-": 6,
                   "R-": 7,
                   "N-": 8,
                   "L-": 9,
                   "Y-": 10,
                   "-O": 11,
                   "-E": 12,
                   "-A": 13,
                   "-U": 14,
                   "-I": 15,
                   "-Ł": 16,
                   "-ᴎ": 17,
                   "-$": 18,
                   "-D": 19,
                   "-C": 20}


class Stroke:
    """A standardized data model for stenotype machine strokes.

    This class standardizes the representation of a stenotype chord. A stenotype
    chord can be any sequence of stenotype keys that can be simultaneously
    pressed. Nearly all stenotype machines offer the same set of keys that can
    be combined into a chord, though some variation exists due to duplicate
    keys. This class accounts for such duplication, imposes the standard
    stenographic ordering on the keys, and combines the keys into a single
    string (called RTFCRE for historical reasons).

    """

    IMPLICIT_HYPHEN = set(('Y'))

    def __init__(self, steno_keys) :
        """Create a steno stroke by formatting steno keys.

        Arguments:

        steno_keys -- A sequence of pressed keys.

        """
        # Remove duplicate keys and save local versions of the input
        # parameters.
        steno_keys_set = set(steno_keys)
        steno_keys = list(steno_keys_set)

        # Order the steno keys so comparisons can be made.
        steno_keys.sort(key=lambda x: STENO_KEY_ORDER.get(x, -1))

        # Convert strokes involving the number bar to numbers.
        if '#' in steno_keys:
            numeral = False
            for i, e in enumerate(steno_keys):
                if e in STENO_KEY_NUMBERS:
                    steno_keys[i] = STENO_KEY_NUMBERS[e]
                    numeral = True
            if numeral:
                steno_keys.remove('#')

        if steno_keys_set & self.IMPLICIT_HYPHEN:
            self.rtfcre = ''.join(key.strip('-') for key in steno_keys)
        else:
            pre = ''.join(k.strip('-') for k in steno_keys if k[-1] == '-' or
                          k == '#')
            post = ''.join(k.strip('-') for k in steno_keys if k[0] == '-')
            self.rtfcre = '-'.join([pre, post]) if post else pre

        self.steno_keys = steno_keys

        # Determine if this stroke is a correction stroke.
        self.is_correction = (self.rtfcre == '-Ul$C')

    def __str__(self):
        if self.is_correction:
            prefix = '-Ul$C'
        else:
            prefix = ''
        return '%sStroke(%s : %s)' % (prefix, self.rtfcre, self.steno_keys)

    def __eq__(self, other):
        return (isinstance(other, Stroke)
                and self.steno_keys == other.steno_keys)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str(self)
