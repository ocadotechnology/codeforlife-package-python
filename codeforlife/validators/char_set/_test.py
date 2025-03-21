"""
© Ocado Group
Created on 21/03/2025 at 18:59:53(+00:00).
"""

from string import ascii_lowercase, ascii_uppercase, digits

# pylint: disable=invalid-name
unicode_lowercase = ascii_lowercase + "αβγδεζηθικλμνξοπρστυφχψω"  # greek
unicode_uppercase = ascii_uppercase + "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"  # greek
unicode_letters = unicode_lowercase + unicode_uppercase
unicode_numbers = digits + "٠١٢٣٤٥٦٧٨٩"  # arabic
# pylint: enable=invalid-name
