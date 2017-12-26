import unittest

import requests.models

from tests.compat import html_escape
from tests.utils import multiline_string

from htmldammit.integrations.requests import get_response_html


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

        response = requests.models.Response()
        response.status_code = 200
        response._content = html.encode('ascii')

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
                response = requests.models.Response()
                response.status_code = 200
                response._content = html.encode(encoding)
                if http_header_encoding is not None:
                    response.headers['Content-Type'] = \
                        'text/html; charset={charset}'.format(charset=http_header_encoding)
                else:
                    response.headers['Content-Type'] = 'text/html'
                result_html = get_response_html(response)
                self.assertEqual(
                    result_html, html,
                    msg="encoding={}, http_header_encoding={}".format(
                        encoding, http_header_encoding),
                )
