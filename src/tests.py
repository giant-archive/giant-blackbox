import os
import re
import unittest
import unittest.util
import uuid
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup

run_uuid = uuid.uuid4().hex


class BlackBoxTestCase(unittest.TestCase):
    """
    This is the base test class.
    """

    def setUp(self):
        """
        Setup simply grabs the domain we are testing from the environment variable
        supplied by Bamboo, and makes it ready to use.
        """

        super(BlackBoxTestCase, self).setUp()

        # Get the domain from the environment variable.
        domain = os.getenv("HOSTNAME")
        verify = bool(int(os.getenv('SSL_VERIFY', 1)))

        self.www = bool(int(os.getenv('bamboo_www_check', 1)))

        assert "http://" in domain or 'https://' in domain

        # Make we remove any trailing slash.
        if domain.endswith("/"):
            domain = domain[:-1]

        # We're done with the domain manipulation.
        self.domain = domain
        self.domain_404 = "%s/does-not-exist-%s" % (self.domain, run_uuid)

        # Setup the requests session.
        self.session = requests_cache.CachedSession(backend='memory', cache_name='cache_%s' % run_uuid)
        self.session.timeout = 5
        self.session.verify = verify
        self.session.headers.update({'User-Agent': 'FARM Digital Black Box Test Agent 1.0'})

    def tearDown(self):
        """
        In our tearDown method, we pause between each test. This is a
        really crappy way to prevent overwhelming a site.
        """

    def assertResponseIsOk(self, response, msg=None):
        self.assertTrue(response.ok, msg=msg)

    def assertResponseIsNotFound(self, response, msg=None):
        self.assertTrue(response.status_code, 404)

    def assertResponseRedirectsTo(self, response, expected, msg=None):
        self.assertTrue(response.history, 'No redirection')
        self.assertTrue(expected in response.url, msg=msg)

    def assertResponseMaxRedirects(self, response, maximum, msg=None):
        standard_msg = 'Exceeded maximum number of redirects (%s/%s)' % (
            unittest.util.safe_repr(len(response.history)),
            unittest.util.safe_repr(maximum)
        )
        msg = self._formatMessage(msg, standard_msg)
        self.assertLessEqual(maximum, len(response.history), msg=msg)

    def assertResponseHeadersContains(self, response, header, msg=None):
        self.assertIn(header, response.headers, msg=msg)

    def assertResponseHeaderEquals(self, response, header, value, msg=None):
        self.assertResponseHeadersContains(response, header, msg=msg)
        self.assertEqual(response.headers.get(header, ''), value, msg=msg)

    def assertResponseContains(self, response, text, msg=None):
        self.assertIn(text, response.text, msg=msg)

    def assertResponseDoesNotContain(self, response, text, msg=None):
        self.assertNotIn(text, response.text, msg=msg)


class TestRedirects(BlackBoxTestCase):
    """
    Tests various redirects.
    """

    def test_canonical_redirect(self):

        root_domain = self.domain.replace('http://', '').replace('https://', '').replace('www.', '')
        https = 'https' in self.domain
        urls = []

        # Build a list of urls to check
        for protocol in ['https://', 'http://']:
            urls.append("%s%s" % (protocol, root_domain))
            if self.www:
                urls.append("%swww.%s" % (protocol, root_domain))

        # Pop our final domain
        urls.remove(self.domain)

        # Remove https is we are not running on https
        if not https:
            urls = [url for url in urls if 'https://' not in url]

        for url in urls:
            response = self.session.get(url)
            self.assertResponseIsOk(response)
            self.assertResponseRedirectsTo(response, "%s/" % self.domain)
            self.assertResponseMaxRedirects(response, 1)


class TestStaticFiles(BlackBoxTestCase):
    """
    Tests some of the static content on the site.
    """

    def test_robots_txt_present(self):
        response = self.session.get('%s/robots.txt' % self.domain)
        self.assertResponseIsOk(response)
        self.assertResponseHeadersContains(response, 'content-type', 'text/plain')

    def test_robots_txt_disallow(self):
        """
        Test that we haven't left a redundant "Disallow: /" in robots.txt.
        """
        response = self.session.get('%s/robots.txt' % self.domain)
        self.assertResponseIsOk(response)
        self.assertResponseDoesNotContain(response, "Disallow: /\n")

    def test_favicon(self):
        """
        Tests that a favicon exists
        """

        # First, check the source for a custom favicon declaration
        response = self.session.get(self.domain)

        # Figure out the favicon
        soup = BeautifulSoup(response.content)
        icon_element = soup.find("link", rel=re.compile('.*icon.*'))

        # If we figured out a favicon element, then we'll use that.
        if icon_element:
            icon_url = urljoin(self.domain, icon_element['href'])

        # If we couldn't find a favicon reference in the source, then use the default /favicon.ico
        else:
            icon_url = urljoin(self.domain, '/favicon.ico')

        # Get the favicon
        icon_response = self.session.get(icon_url)
        self.assertResponseIsOk(icon_response)


class TestSitemap(BlackBoxTestCase):
    """
    Tests the sitemap.xml file.
    """

    def test_sitemap(self):
        response = self.session.get('%s/sitemap.xml' % self.domain)
        self.assertResponseIsOk(response)
        self.assertResponseHeadersContains(response, 'content-type', 'xml')
        self.assertResponseContains(response, '<loc>')
        self.assertResponseContains(response, '</loc>')

    def test_sitemap_correct_site_object(self):
        """
        This tests that the sitemap is being generated with the correct Site object.
        We do this by checking for ".wearefarm.com" in the response.
        """

        response = self.session.get('%s/sitemap.xml' % self.domain)
        self.assertResponseIsOk(response)
        self.assertResponseDoesNotContain(response, ".wearefarm.com")

    def test_child_sitemaps(self):
        """
        """
        pass


class TestHeaders(BlackBoxTestCase):
    """
    This tests various response headers.
    """

    def test_gzip_enabled(self):
        if os.getenv("BALCKBOX_TEST_GZIP", False):
            response = self.session.get(self.domain)
            self.assertResponseHeaderEquals(response, 'content-encoding', 'gzip')


class TestResponseCodes(BlackBoxTestCase):
    """
    Tests the response codes.
    """

    def test_200(self):
        response = self.session.get(self.domain)
        self.assertResponseIsOk(response)
        self.assertResponseHeadersContains(response, 'content-type', 'text/html')

    def test_404(self):
        response = self.session.get(self.domain_404)
        self.assertResponseIsNotFound(response)


class TestDjangoConfig(BlackBoxTestCase):
    """
    Tests that a Django site is configured correctly.
    """

    def test_debug_off(self):
        """
        Here we test that DEBUG isn't enabled, by looking for the string
        "Django" in the 404 response. This might be naive, but it works.
        """
        response = self.session.get(self.domain_404)
        self.assertResponseDoesNotContain(response, "Django")
