from tests.compat import unittest

from htmldammit.contenttypes import get_content_type, ContentTypeHeader


class TestContentTypeHeader(unittest.TestCase):
    def test_sample_headers(self):
        sample_headers = [
            # (header, is_html, is_xml, charset)
            ('text/html', True, False, None),
            ('text/html; charset=utf-8', True, False, 'utf-8'),
            ('text/html; charset=utf-8; something after', True, False, 'utf-8'),
            ('text/html; something before; charset=utf-8', True, False, 'utf-8'),
            ('text/html; something before; charset=utf-8; something after', True, False, 'utf-8'),
            ('text/html; charset=ISO-8859-1', True, False, 'ISO-8859-1'),
            ('text/xml', False, True, None),
            ('application/xhtml+xml', False, True, None),
            ('application/i_just_made_this_up+xml', False, True, None),
            ('text/plain', False, False, None),
            ('W#&%)@(#*&%M', False, False, None),
        ]
        for (header, is_html, is_xml, charset) in sample_headers:
            content_type_header = ContentTypeHeader(header)
            self.assertEqual(is_html, content_type_header.is_html)
            self.assertEqual(is_xml, content_type_header.is_xml)
            self.assertEqual(charset, content_type_header.charset)


class TestGetContentType(unittest.TestCase):
    def test_without_headers(self):
        self.assertEqual(None, get_content_type(None))
        self.assertEqual(None, get_content_type({}))
        self.assertEqual(None, get_content_type({
            'Content-Length': '42',
        }))

    def test_case_insensitivity(self):
        self.assertEqual('VALUE', get_content_type({'Content-Type': 'VALUE'}))
        self.assertEqual('VALUE', get_content_type({'content-type': 'VALUE'}))
        self.assertEqual('VALUE', get_content_type({'CONTENT-TYPE': 'VALUE'}))
        self.assertEqual('VALUE', get_content_type({'CoNtEnT-tYpE': 'VALUE'}))

    def test_with_Message_headers(self):
        """Test with headers given via custom, dict-like "Message" classes.

        The classes tested are httplib.HTTPMessage and rfc822.Message.

        urllib2.urlopen() returns objects whose 'headers' attribute is a
        httplib.HTTPMessage instance, so these objects are what we would
        normally expect to be used. rfc822.Message is the base-class which
        several such "Message" classes inherit from, and therefore should be
        supported.
        """
        try:
            import rfc822
            rfc822_Message = rfc822.Message
        except ImportError:
            rfc822_Message = None
        from htmldammit.contenttypes import \
            CLASSES_WITH_CASE_INSENSITIVE_HEADERS


        for message_class in list(CLASSES_WITH_CASE_INSENSITIVE_HEADERS) + [dict]:
            if rfc822_Message is not None and issubclass(message_class, rfc822_Message):
                from six.moves import StringIO
                _message_class = message_class
                message_class = lambda: _message_class(StringIO())

            # test with various values for the Content-Type header
            for content_type in [
                'text/html',
                'text/html; charset=utf-8',
                ')(Q*&POIP)',
            ]:
                http_headers = message_class()
                http_headers['Content-Type'] = content_type
                self.assertEqual(content_type, get_content_type(http_headers))

            # test with an unrelated header
            http_headers = message_class()
            http_headers['Content-Length'] = '1234'
            self.assertEqual(None, get_content_type(http_headers))

            # test with several headers, including content-length
            http_headers = message_class()
            http_headers['Content-Length'] = '1234'
            http_headers['Content-Type'] = 'VALUE'
            self.assertEqual('VALUE', get_content_type(http_headers))

            # test with no headers
            http_headers = message_class()
            self.assertEqual(None, get_content_type(http_headers))
