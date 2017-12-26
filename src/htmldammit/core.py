import bs4
from bs4.dammit import UnicodeDammit, EncodingDetector
try:
    import lxml.etree
    import lxml.html
except:
    lxml = None

from htmldammit.contenttypes import get_content_type, ContentTypeHeader


def make_UnicodeDammit(raw_html, http_headers=None, **kwargs):
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
        charset = content_type_header.charset
    else:
        is_html = False
        charset = None

    encodings_to_try_first = []
    raw_html, bom_encoding = EncodingDetector.strip_byte_order_mark(raw_html)
    if bom_encoding is not None:
        encodings_to_try_first.append(bom_encoding)

    declared_encoding = EncodingDetector.find_declared_encoding(
        raw_html, is_html=is_html, search_entire_document=True)
    if declared_encoding is not None:
        encodings_to_try_first.append(declared_encoding)

    if charset:
        encodings_to_try_first.append(charset)

    return UnicodeDammit(
        raw_html, is_html=is_html,
        override_encodings=encodings_to_try_first,
        **kwargs
    )


def decode_html(raw_html, http_headers=None):
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
    unicode_dammit = make_UnicodeDammit(raw_html, http_headers=http_headers)
    return unicode_dammit.unicode_markup


def make_soup(raw_html, http_headers=None):
    html = decode_html(raw_html, http_headers=http_headers)

    return bs4.BeautifulSoup(html)


def make_lxml_html(raw_html, http_headers=None, base_url=None):
    """get a parsed HTML object, created using lxml.html.fromstring()"""
    if lxml is None:
        raise Exception(
            "lxml is not available; install lxml to use this feature")

    unicode_dammit = make_UnicodeDammit(raw_html, http_headers=http_headers)
    encoding = unicode_dammit.original_encoding

    # don't just use the original raw_html because UnicodeDammit may strip a BOM
    raw_html = unicode_dammit.detector.markup

    parser = lxml.etree.HTMLParser(encoding=encoding)
    return lxml.html.fromstring(raw_html, base_url=base_url, parser=parser)
