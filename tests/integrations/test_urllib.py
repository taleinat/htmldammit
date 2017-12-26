import unittest
import six.moves.urllib.request as urllib_request

import httpretty

from tests.compat import html_escape
from tests.utils import multiline_string

from htmldammit.integrations.urllib import get_response_html, install_html_response_processor

windows1252_chars = set()
latin1_chars = set()
for val in range(0x20, 0x100):
    try:
        char = bytes([val]).decode('windows-1252')
    except UnicodeDecodeError:
        pass
    else:
        windows1252_chars.add(char)

    try:
        char = bytes([val]).decode('latin-1')
    except UnicodeDecodeError:
        pass
    else:
        latin1_chars.add(char)
common_chars = windows1252_chars & latin1_chars
encoding2chars = {
    'windows-1252': windows1252_chars,
    'latin-1': latin1_chars,
    'common': common_chars,
}


class TestGetRequestHtml(unittest.TestCase):
    _AUTO_CONTENT_LENGTH = object()
    # @classmethod
    # def _make_mock_response(cls, html, encoding,
    #                         url='http://www.example.org/',
    #                         headers=_AUTO_CONTENT_LENGTH,
    #                         status_code=200):
    #     raw_html = html.encode(encoding)
    #     if headers is cls._AUTO_CONTENT_LENGTH:
    #         headers = {'Content-Length': len(raw_html)}
    #
    #     response_fd = BytesIO(raw_html)
    #     response_fd.seek(0)
    #     response = urllib_response.addinfourl(response_fd, headers, url, status_code)
    #     return response

    @classmethod
    def _make_urlopen_response(cls, html, encoding,
                               url='http://www.example.org/',
                               headers=_AUTO_CONTENT_LENGTH,
                               status_code=200):
        raw_html = html.encode(encoding)
        if headers is cls._AUTO_CONTENT_LENGTH:
            headers = {'Content-Length': len(raw_html)}

        _orig_allow_net_connect = httpretty.HTTPretty.allow_net_connect
        httpretty.HTTPretty.allow_net_connect = False
        httpretty.enable()
        try:
            httpretty.register_uri(httpretty.GET, url,
                                   body=raw_html,
                                   adding_headers=headers,
                                   status=status_code)
            return urllib_request.urlopen(url)
        finally:
            httpretty.disable()
            httpretty.HTTPretty.allow_net_connect = _orig_allow_net_connect

    def test_ascii_without_declaration(self):
        html = multiline_string(u'''
            <html>
            <head>
                <title>Half</title>
            </head>
            <body>
                <p>ASCII only!</p>
            </body>
            </html>
            ''')
        response = self._make_urlopen_response(html, 'ascii')
        result_html = get_response_html(response)
        self.assertEqual(result_html, html)

    def test_inline_vs_header_charsets(self):
        html_template = multiline_string(u'''
            <html>
            <head>
                <title>Half</title>
                <meta http-equiv="Content-Type" content="text/html; charset="{charset}">
            </head>
            <body>
                <p>{content}</p>
            </body>
            </html>
            ''')
        for encoding in ['utf-8', 'utf-16', 'latin-1', 'windows-1252']:
            for http_header_encoding in ['utf-8', 'utf-16', 'latin-1', 'windows-1252', None]:
                chars = encoding2chars.get(encoding, windows1252_chars | latin1_chars)
                html = html_template.format(
                    charset=encoding,
                    content=html_escape(''.join(sorted(chars))),
                )
                headers = {
                    'Content-Type':
                        'text/html; charset={charset}'.format(charset=http_header_encoding)
                        if http_header_encoding is not None
                        else 'text/html',
                }
                response = self._make_urlopen_response(html, encoding, headers=headers)
                result_html = get_response_html(response)
                self.assertEqual(
                    result_html, html,
                    msg="encoding={}, http_header_encoding={}".format(
                        encoding, http_header_encoding),
                )


class TestInstallOpener(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._orig_allow_net_connect = httpretty.HTTPretty.allow_net_connect
        httpretty.HTTPretty.allow_net_connect = False
        httpretty.enable()
        install_html_response_processor()

    @classmethod
    def tearDownClass(cls):
        urllib_request.install_opener(urllib_request.build_opener())
        httpretty.disable()
        httpretty.HTTPretty.allow_net_connect = cls._orig_allow_net_connect
        del cls._orig_allow_net_connect

    def test_response_object_read_html(self):
        html = 'TESTING \ua778 \u20AC \u2022 \u262e \u61ba'
        httpretty.register_uri(httpretty.GET, 'http://www.example.com/',
                               body=html.encode('utf-8'),
                               adding_headers={'Content-Type': 'text/html; charset=utf-8'})
        response = urllib_request.urlopen('http://www.example.com/')
        self.assertEqual(response.read_html(), html)

    def test_response_object_cant_read_twice(self):
        html = 'TESTING'
        httpretty.register_uri(httpretty.GET, 'http://www.example.com/',
                               body=html.encode('utf-8'),
                               adding_headers={'Content-Type': 'text/html; charset=utf-8'})
        response = urllib_request.urlopen('http://www.example.com/')
        self.assertEqual(response.read_html(), html)
        self.assertFalse(response.read_html())

    def test_inline_vs_header_charsets(self):
        html_template = multiline_string(u'''
            <html>
            <head>
                <title>Half</title>
                <meta http-equiv="Content-Type" content="text/html; charset="{charset}">
            </head>
            <body>
                <p>{content}</p>
            </body>
            </html>
            ''')
        for encoding in ['utf-8', 'utf-16', 'latin-1', 'windows-1252']:
            for http_header_encoding in ['utf-8', 'utf-16', 'latin-1', 'windows-1252', None]:
                chars = encoding2chars.get(encoding, windows1252_chars | latin1_chars)
                html = html_template.format(
                    charset=encoding,
                    content=html_escape(''.join(sorted(chars))),
                )

                headers = {
                    'Content-Type':
                        'text/html; charset={charset}'.format(charset=http_header_encoding)
                        if http_header_encoding is not None
                        else 'text/html',
                }
                httpretty.register_uri(httpretty.GET, 'http://www.example.com/',
                                       body=html.encode(encoding),
                                       adding_headers=headers)
                response = urllib_request.urlopen('http://www.example.com/')

                self.assertEqual(
                    response.read_html(), html,
                    msg="encoding={}, http_header_encoding={}".format(
                        encoding, http_header_encoding),
                )
