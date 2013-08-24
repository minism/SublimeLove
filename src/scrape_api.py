#!/usr/bin/env python
"""Scrape http://www.love2d.org/wiki for API functions,
callbacks, and their arguments. It's not async...
so it takes a few minutes, but thats fine.
It writes to api.txt and callbacks.txt with the following format:
function_A
function_A,arg1,arg2
"""
import urllib2
from BeautifulSoup import BeautifulSoup

BASE_URL = "http://www.love2d.org/wiki"


def get_soup(url):
    """Return the web page for BASE_URL/url

    Arguments:
    url - url suffix attached to base

    Return:
    BeautifulSoup object

    """
    return BeautifulSoup(urllib2.urlopen("%s/%s" % (BASE_URL, url)).read())


def get_function_arguments(function):
    """Get arguments for each function

    Arguments:
    function - function name, ie love.graphics.circle

    Return:
    list of funcion,arg names

    """
    soup = get_soup(function)
    # Id filter
    f_id = lambda x: x and x.startswith('Arguments')
    arg_spans = soup.findAll('span', id=f_id)
    all_args = []
    for arg_span in arg_spans:
        # Break out of span header and get arguments
        first = arg_span.parent.nextSibling.nextSibling
        # None
        if first.name == 'p' and first.text.rstrip().lstrip() == 'None.':
            all_args.append(function)
        # Many enclosed in dl tag
        elif first.name == 'dl':
            # Get all codes and remove types from begining
            args = [code.text[len(code.find('a').text):].split()[0] for code in
                    first.findAll('code')]
            all_args.append("%s,%s" % (function, ','.join(args)))
    return all_args


def main():
    # Get major groups
    soup = get_soup("Main_Page")
    f_id = lambda x: x and x.startswith('n-love.')
    groups = sorted([x.text for x in soup.findAll('li', id=f_id)])
    with open('api.txt', 'w') as api_file:
        for group in groups:
            # Get functions for each group
            soup = get_soup(group)
            # href filter for sub functions
            f_href = lambda x: x and x.startswith('/wiki/%s.' % group)
            api_calls = soup.findAll('a', href=f_href)
            api_calls = sorted(list(set([x.text for x in api_calls])))
            for call in api_calls:
                print call
                # Write each argument combination
                for args in get_function_arguments(call):
                    api_file.write('%s\n' % args)
            api_file.write('\n')

    soup = get_soup("love")
    # Get callbacks and main groups
    callbacks = set(filter(lambda x: x.startswith('love.'),
                           [x.text for x in soup.findAll('a')]))
    # Remove main groups
    callbacks = sorted(list(callbacks.difference(groups)))
    with open('callbacks.txt', 'w') as callback_file:
        for callback in callbacks:
            print callback
            for args in get_function_arguments(callback):
                callback_file.write('%s\n' % args)


if __name__ == '__main__':
    main()
