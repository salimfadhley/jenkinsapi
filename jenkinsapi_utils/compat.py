"""
Module for Python 2 and Python 3 compatibility
"""
import six


def needs_encoding(text):
    """
    Check whether text data is Python 2 unicode variable and needs to be
    encoded
    """
    if not isinstance(text, six.string_types):
        raise ValueError('You could check only string types')

    if six.PY2 and isinstance(text, unicode):
        return True
    return False


def to_string(text, encoding='utf-8'):
    """
    Return string representation for the text. In case of Python 2 and unicode
    do additional encoding before
    """
    encoded_text = text.encode(encoding) if needs_encoding(text) else text
    return str(encoded_text)
