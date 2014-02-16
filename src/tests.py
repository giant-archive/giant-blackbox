import binascii
import time
import os
import requests
from BeautifulSoup import BeautifulSoup

import unittest
from unittest.util import safe_repr


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
        domain = os.getenv("BAMBOO_DOMAIN", False)

        # Make sure it contains http://
        if not "http://" in domain:
            domain = "http://%s" % domain

        # Make we remove any trailing slash.
        if domain.endswith("/"):
            domain = domain[:-1]

        # Make sure we add the 'www' subdomain.
        if not "www." in domain:
            domain = domain.replace("http://", "http://www.")

        # We're done with the domain manipulation.
        self.domain = domain

        # Setup the requests session.
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'FARM Digital Black Box Test Agent 1.0'})


    def tearDown(self):
        """
        In our tearDown method, we pause between each test. This is a
        really crappy to prevent overwhelming a site.
        """

        #time.sleep(4)


    def assertResponseIsOk(self, response, msg=None):
        self.assertTrue(response.ok, msg=msg)


    def assertResponseIsNotFound(self, response, msg=None):
        self.assertTrue(response.status_code, 404)


    def assertResponseRedirectsTo(self, response, expected, msg=None):
        self.assertTrue(response.history, 'No redirection')
        self._baseAssertEqual(response.url, expected, msg=msg)


    def assertResponseMaxRedirects(self, response, maximum, msg=None):
        standard_msg = 'Exceeded maximum number of redirects (%s/%s)' \
                       % (safe_repr(len(response.history)), safe_repr(maximum))
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
        response = self.session.get(self.domain.replace("www.", ""))
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
        self.assertResponseHeaderEquals(response, 'content-type', 'text/plain')


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
        icon_element = soup.find("link", rel="shortcut icon")

        # If we figured out a favicon element, then we'll use that.
        if icon_element:
            icon_url = "%s/%s" % (self.domain, icon_element['href'])

        # If we couldn't find a favicon reference in the source, then use the default /favicon.ico
        else:
            icon_url = "%s/favicon.ico" % self.domain

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


    def test_child_sitemaps(self):
        """
        """
        pass


class TestHeaders(BlackBoxTestCase):
    """
    This tests various response headers.
    """

    def setUp(self):
        super(TestHeaders, self).setUp()


    def test_gzip_enabled(self):
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
        random_junk = binascii.b2a_hex(os.urandom(15))
        response = self.session.get("%s/%s" % (self.domain, random_junk))
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

        random_junk = binascii.b2a_hex(os.urandom(15))
        response = self.session.get("%s/%s" % (self.domain, random_junk))
        self.assertResponseDoesNotContain(response, "Django")
