"""Constants for use in tests."""

import uuid
from os import getenv
from urllib.parse import urlparse


RUN_ID = uuid.uuid4().hex
URL = urlparse(getenv("HOSTNAME"))
SCHEME = URL.scheme + "://"
SSL_VERIFY = bool(int(getenv("SSL_VERIFY", 1)))
TEST_GZIP = getenv("BLACKBOX_TEST_GZIP", False)
