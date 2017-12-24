import re
import textwrap

import six

from tests.compat import unittest, mock
from htmldammit import decode_html, make_UnicodeDammit, make_lxml_html


def multiline_string(s):
    m = re.match(r'^[ \t]*\n', s, re.U)
    if m is not None:
        s = s[m.end():]
    return textwrap.dedent(s)


class TestDecodeHtml(unittest.TestCase):
    def test_just_ascii(self):
        "Test without any Content-Type declaration, with ASCII-only HTML."
        for encoding in ['utf-8', 'utf-16', 'iso-8859-1', 'windows-1252']:
            html = multiline_string(u'''
                <html>
                    <body>
                        <p>Hello ASCII!</p>
                    </body>
                </html>
                ''')
            decoded_html = decode_html(html.encode(encoding))
            self.assertEqual(html, decoded_html)
            self.assertTrue(isinstance(decoded_html, six.text_type))

    def test_with_header_encoding(self):
        "Test with Content-Type decalred in a HTTP response header."
        for encoding in ['utf-8', 'utf-16', 'iso-8859-1', 'windows-1252']:
            http_headers = {'Content-Type': 'text/html; charset=' + encoding}
            html = multiline_string(u'''
                <html>
                    <body>
                        <p>\u00E1</p>
                    </body>
                </html>
                ''')
            self.assertEqual(html, decode_html(html.encode(encoding), http_headers))

    def test_with_meta_equiv_tag(self):
        "Test with Content-Type declared in a <meta http-equiv=...> HTML tag."
        for encoding in ['utf-8', 'utf-16', 'iso-8859-1', 'windows-1252']:
            html = multiline_string(u'''
                <html>
                    <head>
                        <meta http-equiv="Content-Type" content="text/html; charset="{charset}">
                    </head>
                    <body>
                        <p>\u00E1</p>
                    </body>
                </html>
                ''').format(charset=encoding)
            self.assertEqual(html, decode_html(html.encode(encoding),
                                               http_headers={'Content-Type': 'text/html'}))

    def test_with_xhtml_doctype_encoding(self):
        "Test with Content-Type declared in the XML <?xml ...> tag."
        for encoding in ['utf-8', 'utf-16', 'iso-8859-1', 'windows-1252']:
            # lxml.html raises ValueError if given unicode
            # and the document has an XML encoding declaration
            html = multiline_string(u'''
                <?xml version="1.0" encoding="{charset}"?>
                <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    
                <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
                    <head>
                        <title>Half</title>
                    </head>
                    <body>
                        <p>\u00BD</p>
                    </body>
                </html>
                ''').format(charset=encoding)
            self.assertEqual(html, decode_html(html.encode(encoding)))


class MockUnicodeDammit(object):
    NOT_GIVEN = object()

    def __init__(self, raw_html, is_html=NOT_GIVEN, override_encodings=NOT_GIVEN, smart_quotes_to=NOT_GIVEN):
        self.raw_html = raw_html
        self.is_html = is_html
        self.override_encodings = override_encodings
        self.smart_quotes_to = smart_quotes_to


class TestMakeUnicodeDammit(unittest.TestCase):
    def test_no_header(self):
        "Test without any Content-Type declaration, with ASCII-only HTML."
        raw_html = b'BLA'
        http_headers = {}

        # with mock.patch('htmldammit.UnicodeDammit', autospec=True) as mock_ud:
        #     make_UnicodeDammit(raw_html, http_headers)
        #
        # mock_ud.assert_called_with(raw_html, is_html=True,
        #                            override_encodings=[],
        #                            smart_quotes_to='auto')

        ud = make_UnicodeDammit(raw_html, http_headers)
        self.assertEqual(raw_html, ud.unicode_markup.encode(ud.original_encoding))
        self.assertEqual(False, ud.is_html)

    def test_html_header(self):
        raw_html = 'BLA'
        http_headers = {'Content-Type': 'text/html'}

        with mock.patch('htmldammit.UnicodeDammit', MockUnicodeDammit):
            ud = make_UnicodeDammit(raw_html, http_headers)

        self.assertEqual(raw_html, ud.raw_html)
        self.assertEqual(True, ud.is_html)
        self.assertEqual([], ud.override_encodings)
        self.assertEqual('html', ud.smart_quotes_to)

    def test_html_header_with_charset(self):
        for encoding in ['utf-8', 'utf-16', 'iso-8859-1', 'windows-1252']:
            raw_html = 'BLA'
            http_headers = {'Content-Type': 'text/html; charset={charset}'.format(charset=encoding)}

            with mock.patch('htmldammit.UnicodeDammit', MockUnicodeDammit):
                ud = make_UnicodeDammit(raw_html, http_headers)

            self.assertEqual(raw_html, ud.raw_html)
            self.assertEqual(True, ud.is_html)
            self.assertEqual([encoding], ud.override_encodings)
            self.assertEqual('html', ud.smart_quotes_to)

    def test_xhtml_header(self):
        raw_html = 'BLA'
        http_headers = {'Content-Type': 'application/xhtml+xml'}

        with mock.patch('htmldammit.UnicodeDammit', MockUnicodeDammit):
            ud = make_UnicodeDammit(raw_html, http_headers)

        self.assertEqual(raw_html, ud.raw_html)
        self.assertEqual(False, ud.is_html)
        self.assertEqual([], ud.override_encodings)
        self.assertEqual('xml', ud.smart_quotes_to)

    def test_text_plain_header(self):
        raw_html = b'BLA'
        http_headers = {'Content-Type': 'text/plain'}

        with mock.patch('htmldammit.UnicodeDammit', MockUnicodeDammit):
            ud = make_UnicodeDammit(raw_html, http_headers)

        self.assertEqual(raw_html, ud.raw_html)
        self.assertEqual(False, ud.is_html)
        self.assertEqual([], ud.override_encodings)
        self.assertEqual('ascii', ud.smart_quotes_to)


class TestLxmlHtml(unittest.TestCase):
    # def test_encoding(self):
    #     http_headers = {b'Content-Type': b'text/html; charset=utf-8'}
    #     uh = UnicodeHTML(b'NO DATA', http_headers=http_headers)
    #     self.assertEqual('utf-8', uh.encoding)
    #
    #     http_headers = {b'Content-Type': b'text/html; charset=latin-1'}
    #     uh = UnicodeHTML(b'NO DATA', http_headers=http_headers)
    #     self.assertEqual('latin-1', uh.encoding)
    #
    #     http_headers = {b'Content-Type': b'text/html'}
    #     uh = UnicodeHTML(b'NO DATA', http_headers=http_headers)
    #     self.assertEqual('ascii', uh.encoding)
    #
    # def test_unicode_html(self):
    #     http_headers = {b'Content-Type': b'text/html; charset=utf-8'}
    #     uh = UnicodeHTML(b'NO DATA', http_headers=http_headers)
    #     self.assertTrue(isinstance(uh.unicode_html, six.text_type))
    #
    def test_parsed_ascii(self):
        raw_html = b'<html><body><p>Text</p></body></html>'
        http_headers = {'Content-Type': 'text/html; charset=utf-8'}
        parsed = make_lxml_html(raw_html, http_headers)
        self.assertEqual(u'Text', parsed.xpath('//p/text()')[0])

    def test_parsed_nonascii(self):
        raw_html = u'<html><body><p>\u20AA</p></body></html>'
        http_headers = {'Content-Type': 'text/html; charset=utf-8'}
        parsed = make_lxml_html(raw_html, http_headers)
        self.assertEqual(u'\u20AA', parsed.xpath('//p/text()')[0])

    def test_with_doctype_encoding(self):
        # lxml.html (used by lxmlHTMLParser) raises ValueError if given unicode
        # and the document has an XML encoding declaration
        html = multiline_string(u'''
            <?xml version="1.0" encoding="utf-8"?>
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
              "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
            <head>
                <title>Money!</title>
            </head>
            <body>
                <p>\u20AA</p>
            </body>
            </html>
            ''')
        encoded_html = html.encode("utf-8")

        parsed = make_lxml_html(encoded_html)
        self.assertEqual(u'\u20AA', parsed.xpath('//p/text()')[0])
