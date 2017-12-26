from htmldammit.core import decode_html, make_UnicodeDammit


def get_response_html(response):
    return decode_html(response.content, http_headers=response.headers)


def request_hook(response, **kwargs):
    stream = kwargs.get('stream', False)
    if stream:
        return

    ud = make_UnicodeDammit(response.content, response.headers)
    response.encoding = ud.original_encoding
    response._content = ud.detector.markup
    return response


# def install_default_request_hook():
#     import requests.hooks
#     import requests.models
#
#     orig_default_hooks = requests.hooks.default_hooks
#     def default_hooks():
#         d = orig_default_hooks()
#         d.setdefault('response', []).append(request_hook)
#         return d
#
#     requests.hooks.default_hooks = default_hooks
#     requests.models.default_hooks = default_hooks
