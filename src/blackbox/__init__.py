"""Base Test class and shared attributes."""

import requests_cache

from blackbox.constants import RUN_ID, SSL_VERIFY, URL, SCHEME


class BlackBoxBase:
    """Base test class for all blackbox tests."""

    session = requests_cache.CachedSession(
        backend="memory",
        cache_name=f"cache_{RUN_ID}"
    )
    session.timeout = 5
    session.verify = SSL_VERIFY
    session.headers.update({"User-Agent": "FARM Digital Black Box Test Agent 1.0"})

    @classmethod
    def setup_class(cls):
        """Parse the provided hostname, and set test-wide attributes."""
        assert URL.scheme, "URL must contain a valid scheme (http:// or https://)"
        cls.root = f"{SCHEME}{URL.hostname}"
        cls.random_url = f"{cls.root}/does-not-exist-{RUN_ID}"
