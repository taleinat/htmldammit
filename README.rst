======================
htmldammit
======================

.. image:: https://img.shields.io/pypi/v/htmldammit.svg?style=flat
    :target: https://pypi.python.org/pypi/htmldammit
    :alt: Latest Version

.. image:: https://img.shields.io/travis/taleinat/htmldammit/master.svg?style=flat
    :target: https://travis-ci.org/taleinat/htmldammit
    :alt: Build & Tests Status

.. image:: https://img.shields.io/coveralls/taleinat/htmldammit/master.svg?style=flat
    :target: https://coveralls.io/r/taleinat/htmldammit
    :alt: Test Coverage

.. image:: https://img.shields.io/pypi/l/htmldammit.svg?style=flat
    :target: https://github.com/taleinat/htmldammit/blob/master/LICENSE
    :alt: License: MIT

Make every effort to properly decode HTML, because HTML is unicode, dammit!

Features
--------

* Very easy to use with integrations for ``requests`` and ``urlopen()``.
* Utilizes information from HTTP headers, inline encoding declarations,
  and UTF BOM-s (Byte Order Marks), as well as falling back to making a
  best guess based on the raw data.
* Improves upon BeautifulSoup's great ``UnicodeDammit`` utility.

Installation
------------

.. code::

    pip install htmldammit

Additionally, it is *highly* recommended to install the ``cchardet`` and/or
the ``chardet`` libraries. This will enable the fallback to guessing the
encoding based on the raw data.

.. code::

    pip install cchardet chardet

Basic usage
-----------

To decode any binary HTML content into unicode (passing HTTP headers is optional):

.. code:: python

    from htmldammit import decode_html
    html = decode_html(raw_html, http_headers)

To get unicode HTML from a ``requests`` response:

.. code:: python

    from htmldammit.integrations.requests import get_response_html
    response = requests.get('http://www.example.org/')
    html = get_response_html(response)

To get unicode HTML from a ``urlopen()`` response:

.. code:: python

    from htmldammit.integrations.urllib import get_response_html
    response = urlopen('http://www.example.org/')
    html = get_response_html(response)
