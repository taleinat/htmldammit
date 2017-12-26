import re
import textwrap


__all__ = ['multiline_string']


def multiline_string(s):
    m = re.match(r'^[ \t]*\n', s, re.U)
    if m is not None:
        s = s[m.end():]
    return textwrap.dedent(s)
