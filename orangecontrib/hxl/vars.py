# orangecontrib/hxl/vars.py


import os
from pathlib import Path

# Unless DATAVAULT_BASE is set, we use '~/.orange3data' for everything
DATAVAULT_BASE = os.environ.get(
    'DATAVAULT_BASE',
    f'{Path.home()}/.orange3data'
)
INFIX_INPUT_RAWFILE = 'rawinput'
INFIX_INPUT_RAWTRANSFILE = 'transformedinput'
INFIX_INPUT_RAWUNCOMPFILE = 'unzipedinput'
INFIX_INPUT_RAWTEMP = 'inputtemp'

# HTTP status, how to react _________________________________________________
# for already locally cached resource, response code like this means erase
# local caches compatible with how sensitive content was marked initially
HTTP_STATUS_HARDFAIL = [
    401,  # 401 Unauthorized
    403,  # 403 Forbidden
    404,  # 404 Not Found
    405,  # 405 Method Not Allowed
    406,  # 406 Not Acceptable
    407,  # 407 Proxy Authentication Required
    408,  # 408 Request Timeout
    409,  # 409 Conflict
    410,  # 410 Gone
    418,  # 418 I'm a teapot
    451,  # 451 Unavailable For Legal Reasons
]

# These responses may mean temporary error, but not strong hint to delete
# local caches without user feedback
HTTP_STATUS_SOFTFAIL = [
    400,  # 400 Bad Request
    411,  # 411 Length Required
    412,  # 412 Precondition Failed
    413,  # 413 Payload Too Large
    414,  # 414 URI Too Long
    415,  # 415 Unsupported Media Type
    416,  # 416 Requested Range Not Satisfiable
    417,  # 417 Expectation Failed
    425,  # 425 Too Early
    426,  # 426 Upgrade Required
    428,  # 428 Precondition Required
    429,  # 429 Too Many Requests
    500,  # 500 Internal Server Error
    501,  # 501 Not Implemented
    502,  # 502 Bad Gateway
    503,  # 503 Service Unavailable
    504,  # 504 Gateway Timeout
    505,  # 505 HTTP Version Not Supported
    506,  # 506 Variant Also Negotiates
    507,  # 507 Insufficient Storage
    508,  # 508 Loop Detected (WebDAV (en-US))
    510,  # 510 Not Extended
    511,  # 511 Network Authentication Required
]
