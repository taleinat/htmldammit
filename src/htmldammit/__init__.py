"""A library for decoding HTML fetched from the web into Unicode.

Uses BeautifulSoup4.UnicodeDammit internally. It, in turn, uses the 'chardet'
module internally if it is available, which is recommended.

It is highly recommended to use the HTTP response headers if they are available,
since often the correct encoding is described in the 'Content-Type' header.

Note that lxml.html recommends not passing HTML as unicode. Rather, the best
option is to pass the raw (encoded) HTML, and the correct encoding. This is
all taken care of by the UnicodeHTML.get_parsed() method; use it!

A utility function, decode_html(), is supplied:

html = decode_html(raw_html, http_headers)
"""
__version__ = '0.1.0a0'
__all__ = ['decode_html', 'make_lxml_html', 'make_soup']

from htmldammit.core import decode_html, make_lxml_html, make_soup
