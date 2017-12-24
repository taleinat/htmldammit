"""Module for decoding HTML fetched from the web into Unicode.

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
__all__ = ['decode_html', 'make_lxml_html', 'make_soup',
           'get_requests_response_text']

import bs4
from bs4.dammit import UnicodeDammit, EncodingDetector
try:
    import lxml.etree
    import lxml.html
except:
    lxml = None

from htmldammit.contenttypes import get_content_type, ContentTypeHeader


def make_UnicodeDammit(raw_html, http_headers=None,
                       smart_quotes_to='auto', **kwargs):
    """create a UnicodeDammit instance for the given HTML

    If given the HTTP response headers and they contain a Content-Type header
    with an encoding, it will be given to UnicodeDammit properly.

    @param raw_html: the binary (i.e. encoded) HTML data (str)
    @param http_headers: the HTTP response headers (dict; optional)
    @return: a UnicodeDammit instance
    """
    content_type = get_content_type(http_headers)
    if content_type:
        content_type_header = ContentTypeHeader(content_type)
        is_html = content_type_header.is_html
        # also detect XML in order to support XHTML properly
        is_xml = content_type_header.is_xml
        charset = content_type_header.charset
    else:
        is_html = False
        is_xml = False
        charset = None

    if smart_quotes_to == 'auto':
        smart_quotes_to = 'html' if is_html else 'xml' if is_xml else 'ascii'

    if charset:
        encoding_detector = EncodingDetector(raw_html, is_html=is_html)
        encodings_to_try_first = [
            encoding_detector.sniffed_encoding,
            encoding_detector.declared_encoding,
            charset,
        ]
        encodings_to_try_first = \
            [enc for enc in encodings_to_try_first if enc is not None]
    else:
        encodings_to_try_first = []

    return UnicodeDammit(
        raw_html, is_html=is_html,
        override_encodings=encodings_to_try_first,
        smart_quotes_to=smart_quotes_to,
        **kwargs
    )


def decode_html(raw_html, http_headers=None, smart_quotes_to='auto'):
    """Decode binary HTML data into unicode.

    An encoding definition is looked for in the document itself and in the
    Content-Type HTTP header. Inline declarations are preferred over the
    Content-Type header. If no encoding declaration is found, the best encoding
    is guessed according to the data.

    Important note: *If installed*, the 'cchartdet' or 'chardet' libraries
    will be used to detect the encoding if no declaration is found. Therefore,
    for best results, it is highly recommended to have at least on of these
    installed.

    Notes:
    * XHTML is supported

    @param raw_html: the binary (i.e. encoded) HTML data (str)
    @param http_headers: the HTTP response headers (dict; optional)
    @return: the given HTML data, decoded (unicode)
    """
    unicode_dammit = make_UnicodeDammit(raw_html, http_headers=http_headers,
                                        smart_quotes_to=smart_quotes_to)
    return unicode_dammit.unicode_markup


def make_soup(raw_html, http_headers=None, smart_quotes_to='auto'):
    html = decode_html(raw_html, http_headers=http_headers,
                       smart_quotes_to=smart_quotes_to)

    return bs4.BeautifulSoup(html)


def make_lxml_html(raw_html, http_headers=None, base_url=None,
                   smart_quotes_to='auto'):
    """get a parsed HTML object, created using lxml.html.fromstring()"""
    if lxml is None:
        raise Exception(
            "lxml is not available; install lxml to use this feature")

    unicode_dammit = make_UnicodeDammit(raw_html, http_headers=http_headers,
                                        smart_quotes_to=smart_quotes_to)
    encoding = unicode_dammit.original_encoding

    # don't just use the original raw_html because UnicodeDammit may strip a BOM
    raw_html = unicode_dammit.detector.markup

    parser = lxml.etree.HTMLParser(encoding=encoding)
    return lxml.html.fromstring(raw_html, base_url=base_url, parser=parser)


def get_requests_response_text(response):
    return decode_html(response.content, http_headers=response.headers)
