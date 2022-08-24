# orangecontrib/hxl/vars.py


import os
from pathlib import Path

# Data Vault local storage __________________________________________________

# Unless DATAVAULT_BASE is set, we use '~/.orange3data' for everything
DATAVAULT_BASE = os.environ.get(
    'DATAVAULT_BASE',
    f'{Path.home()}/.orange3data'
)
INFIX_INPUT_RAWFILE = 'rawinput'
INFIX_INPUT_RAWTRANSFILE = 'transformedinput'
INFIX_INPUT_RAWUNCOMPFILE = 'unzipedinput'
INFIX_INPUT_RAWTEMP = 'inputtemp'

# Requests via API; identification __________________________________________
# @see https://www.mediawiki.org/wiki/API:Etiquette
# ini_set('user_agent', 'MyCoolTool/1.1 (https://example.org/MyCoolTool/; MyCoolTool@example.org) UsedBaseLibrary/1.4');
_VERSION = "0.3.1rc1"
_BOTPOLICYLINK = "https://github.com/fititnt/orange3-hxl"  # @TODO needs to be updated

USER_CONTACT_MAIL = os.environ.get(
    'USER_CONTACT_MAIL',
    'anonymous@example.org'
)
GENERIC_CONTACT_MAIL = os.environ.get(
    'GENERIC_CONTACT_MAIL',
    'anonymous@example.org'
)

HTTP_USER_AGENT__AUTH = f'Orange3-HXLvisualETL/{_VERSION} ({_BOTPOLICYLINK}; {USER_CONTACT_MAIL})'
HTTP_USER_AGENT__GENERIC = ''

# Requests via API; limits ____________________________________________________
# @TODO this part if a draft; requires responsible GUI issue solved
#       (https://github.com/fititnt/orange3-hxl/issues/3)
THROTTLING_AUTHENTICAED_DEFAULT = 60
THROTTLING_AUTHENTICAED_MINIMUM = 10

THROTTLING_GENERIC_DEFAULT = 60
THROTTLING_GENERIC_MINIMUM = 60


# Resource options _________________________________________________________
RESOURCE_DATAVAULT_CACHING_KIND__HELP = """
Kind of resource. Please set it to the public if resources have no personal
information and checking new versions from source can overload servers.
"""
RESOURCE_DATAVAULT_CACHING_KIND = {
    'unknown': 0,
    'public data': 10,
    'sensitive data': -10,
    # 'sensitive++': -20,  # @TODO disk encryption for cached files with trow-away key usable while app not closed (or crashed)
}
RESOURCE_DATAVAULT_CACHE_TTL__HELP = """
Default time the resource will be considered new, without trying to check
servers for updates.
"""
RESOURCE_DATAVAULT_CACHE_TTL = {
    '1 month': 2629800,
    '1 week': 604800,
    '3 days': 259200,
    '1 day': 86400,
    '12 hours': 43200,
    '1 hour': 3600,
    # '': 0,
}

# HTTP status, how to react ___________________________________________________
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

# Even for resources marked as public, these codes are unlikely to be
# misconfiguration or network error. Ideally we should add autehentication
# fails here too, but at the moment the extension does not support then.
HTTP_STATUS_ALWAYSFAIL = [
    410,  # 410 Gone
    451,  # 451 Unavailable For Legal Reasons
]
