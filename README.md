# giant-blackbox

This is a simple test suite which runs some black-box tests on a given website. It's designed to provide sanity checks as part of a post-deployment workflow.

Further Reading: http://en.wikipedia.org/wiki/Black-box_testing

## Introduction

This software was designed with the following considerations in mind:

- It should be run via a Github action.
- It should take a single required argument, a hostname, and not require any further information about a given domain.
- The tests should behave well, so as to not overwhelm the application server.

## TODO

- This should report to a Slack webhook.
- It might be worth investigating changing from `unittest`-derived tests to something lighter with pytest.

## Dependencies

- pytest, for use as a nicer test runner than UnitTest.
- BeautifulSoup4

## Setup

As part of a Github `workflow.yml` file:

    - name: Run live site checks
      uses: giantmade/giant-blackbox
      with:
        hostname: "https://www.example.com"
        verify_ssl: "True"

## Credits

The first version of this code was written in [Leon Smith's gist](https://gist.github.com/leonsmith/75ed9c221fde3bf17d4f). Everything since then has been rearranging code around the edges. Thank you Leon. 