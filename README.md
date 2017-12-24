# htmldammit

Make every effort to properly decode HTML, because HTML is unicode, dammit!

## Installation

`pip install htmldammit`

Additionally, it is _highly_ recommended to install the `cchardet` and/or
the `chardet` libraries:

`pip install cchardet chardet`

## Basic usage

`html = decode_html(raw_html, http_headers)`
