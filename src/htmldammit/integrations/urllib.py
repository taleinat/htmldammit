import six.moves.urllib.request as urllib_request

from htmldammit.contenttypes import get_content_type, ContentTypeHeader
from htmldammit.core import decode_html


def get_response_html(response):
    return decode_html(response.read(), response.info())


class HtmlResponse(object):
    def __init__(self, addinfourl_obj):
        self.__addinfourl_obj = addinfourl_obj

    def __getattr__(self, name):
        return getattr(self.__addinfourl_obj, name)

    def __enter__(self):
        return self.__addinfourl_obj.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.__addinfourl_obj.__exit__(exc_type, exc_val, exc_tb)

    def __iter__(self):
        return iter(self.__addinfourl_obj)

    def read_html(self):
        return decode_html(self.read(), self.info())


class HtmlResponseProcessor(urllib_request.BaseHandler):
    """Process HTML responses and decode the content as Unicode."""
    def http_response(self, request, response):
        content_type_header = ContentTypeHeader(get_content_type(response.info()))
        if content_type_header is not None and content_type_header.is_html:
            return HtmlResponse(response)

        return response

    https_response = http_response


def install_html_response_processor():
    urllib_request.install_opener(
        urllib_request.build_opener(
            HtmlResponseProcessor()
        )
    )
