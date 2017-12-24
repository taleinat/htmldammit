import re
import email.message

CLASSES_WITH_CASE_INSENSITIVE_HEADERS = (email.message.Message,)
HTTP_RESPONSE_CLASSES = tuple()

try:
    import rfc822
except ImportError:
    pass
else:
    CLASSES_WITH_CASE_INSENSITIVE_HEADERS += (rfc822.Message,)

try:
    import http.client
except ImportError:
    pass
else:
    CLASSES_WITH_CASE_INSENSITIVE_HEADERS += (http.client.HTTPMessage,)
    HTTP_RESPONSE_CLASSES += (http.client.HTTPResponse,)

try:
    import httplib
except ImportError:
    pass
else:
    CLASSES_WITH_CASE_INSENSITIVE_HEADERS += (httplib.HTTPMessage,)
    HTTP_RESPONSE_CLASSES += (httplib.HTTPResponse,)

try:
    import requests
except ImportError:
    pass
else:
    CLASSES_WITH_CASE_INSENSITIVE_HEADERS += (requests.structures.CaseInsensitiveDict,)
    HTTP_RESPONSE_CLASSES += (requests.Response,)


class ContentTypeHeader(object):
    "Keeps the value of an HTTP Content-Type header, and gives info about it."

    HTML_CONTENT_TYPE = 'text/html'
    XHTML_CONTENT_TYPE = 'application/xhtml+xml'
    XML_CONTENT_TYPES = (XHTML_CONTENT_TYPE,) + ('text/xml', 'application/xml')

    def __init__(self, header_value):
        """
        @param header_value: value of the Content-Type header, e.g. "text/html"
        """
        self.header_value = header_value
        self._first_part_lower = self.header_value.split(';', 1)[0].lower()

    @property
    def is_html(self):
        "Tell whether the header says that the content is HTML."
        return self._first_part_lower.startswith(self.HTML_CONTENT_TYPE)

    @property
    def is_xml(self):
        "Tell whether the header says that the content is XML."
        return (
            self._first_part_lower.startswith(self.XML_CONTENT_TYPES) or
            (
                self._first_part_lower.startswith('application/') and
                self._first_part_lower.endswith('+xml')
            )
        )

    @property
    def charset(self):
        'Fetch the "charset" from the header value, or None if not found.'
        m = re.search(r'charset=([^;]+)', self.header_value, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        else:
            return None


def get_content_type(http_headers):
    "fetch the Content-Type header's value, or None if no such header is found"
    header_value = None

    if http_headers is not None:
        # most message classes, e.g. rfc822.Message and email.message.Message,
        # are dict-like but use case-insensitive matching
        header_value = http_headers.get('content-type', None)
        if header_value is None:
            if not isinstance(http_headers,
                              CLASSES_WITH_CASE_INSENSITIVE_HEADERS):
                for header_name in http_headers:
                    if header_name.lower() == 'content-type':
                        header_value = http_headers[header_name]
                        break

    return header_value
