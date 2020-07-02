import re
from urllib.parse import urljoin

import pytest
from bs4 import BeautifulSoup

from tests import BlackBoxBase, checks
from constants import URL, TEST_GZIP


class TestRedirects(BlackBoxBase):
    """Tests various redirects."""

    def test_canonical_redirect(self):
        """"""
        urls = (protocol + URL.hostname for protocol in {"http://", URL.scheme})
        for url in urls:
            response = self.session.get(url)
            checks.response_code(response, 200)
            checks.maximum_redirects(response, 1)


class TestStaticFiles(BlackBoxBase):
    """Tests some of the static content on the site."""

    def test_robots_txt_present(self):
        response = self.session.get("{self.root}/robots.txt")
        checks.response_code(response, 200)
        checks.has_header(response, "content-type", "text/plain")

    def test_robots_txt_disallow(self):
        """Test that we haven't left a redundant "Disallow: /" in robots.txt."""
        response = self.session.get(f"{URL.domain}/robots.txt")
        checks.response_code(response, 200)
        checks.response_not_contains(response, "Disallow: /")

    def test_favicon(self):
        """Tests that a favicon exists."""
        # First, check the source for a custom favicon declaration
        response = self.session.get(self.domain)

        # Figure out the favicon
        soup = BeautifulSoup(response.content, features="html5lib")
        icon_element = soup.find("link", rel=re.compile('.*icon.*'))

        # If we figured out a favicon element, then we'll use that.
        icon_url = urljoin(self.root, '/favicon.ico')
        if icon_element:
            icon_url = urljoin(self.root, icon_element['href'])

        # Get the favicon
        icon_response = self.session.get(icon_url)
        checks.response_code(icon_response, 200)


class TestSitemap(BlackBoxBase):
    """Tests the sitemap.xml file."""

    def test_sitemap(self):
        response = self.session.get(f"{self.root}/sitemap.xml")
        checks.response_code(response, 200)
        checks.header_equals(response, "content-type", "xml")
        checks.response_contains(response, "sitemaps.org/schema")

    def test_sitemap_correct_site_object(self):
        """
        This tests that the sitemap is being generated with the correct Site object.
        We do this by checking for ".wearefarm.com" in the response.
        """
        response = self.session.get(f"{self.root}/sitemap.xml")
        checks.response_code(response, 200)
        checks.response_not_contains(response, ".wearefarm.com")


class TestHeaders(BlackBoxBase):
    """This tests various response headers."""

    @pytest.mark.skipif(not TEST_GZIP, reason="BLACKBOX_TEST_GZIP variable required.")
    def test_gzip_enabled(self):
        """Ensure that the site is using gzip."""
        response = self.session.get(self.root)
        checks.header_equals(response, "content-encoding", "gzip")


class TestResponseCodes(BlackBoxBase):
    """Tests the response codes."""

    def test_200(self):
        """Ensure that GET requests to the index view return 200."""
        response = self.session.get(self.root)
        checks.response_code(response, 200)
        checks.header_equals(response, "content-type", "text/html")

    def test_404(self):
        """Ensure that GET requests to nonexistent URLs return 404"""
        response = self.session.get(self.random_url)
        checks.response_code(response, 404)


class TestDjangoConfig(BlackBoxBase):
    """Tests that a Django site is configured correctly."""

    def test_debug_off(self):
        """
        Here we test that DEBUG isn't enabled, by looking for the string
        "Traceback" in the 404 response. This might be naive, but it works.
        """
        response = self.session.get(self.random_url)
        checks.response_not_contains(response, "Traceback")
