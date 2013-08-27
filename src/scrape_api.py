#!/usr/bin/env python
"""Scrape http://www.love2d.org/wiki for API functions, callbacks, arguments.

It's not async...so it takes a few minutes, but thats fine.
It writes to api.txt and callbacks.txt with the following format:
function_A
function_A,arg1,arg2

The code filters everything by the specified API version.

"""
import csv
import sys
import urllib
import urllib2

import mwparserfromhell
import simplejson


def get_functions(api_version):
    """Get functions filtered by api version
    Thanks go to tonyb486 for the mediawiki hint

    Arguments:
    api_version - int

    Return:
    [functions, callbacks] - two length array of array of strings

    """
    results = [[], []]

    args = {
        "title": "Special:Ask",
        "order_num": "ASC",
        "p[format]": "csv",
        "p[limit]": "500",
        "eq": ["yes", "yes"],
        "po": "?parent\r\n?Since\r\n?Removed\r\n"
    }
    
    qs = ["[[Category:Functions]]\r\n[[parent::~love.*]]\r\n[[parent::!~*(*]]",
          "[[Category:Callbacks]]\r\n[[parent::love]]"]

    for i, q in enumerate(qs):
        args["q"] = q
        csv_data =  urllib.urlopen("http://www.love2d.org/wiki/Special:Ask",
                                   urllib.urlencode(args)).readlines()
        # Get array of rows and remove header
        data = list(csv.reader(csv_data, delimiter=",", quotechar="\""))[1:]

        # TODO: pagination if we ever reach single request limit
        if len(data) == 500:
            raise Exception("500 results - possibly truncated. Please fix me")

        for function, parent, since, removed in data:
            # Since can have multiple values? WHY? So split on , and get last
            since = 0 if since == '' else int(since.split(',')[-1])
            # Same here - split on , and get last
            removed = float('inf') if removed == '' else \
                      int(removed.split(',')[-1])
            if since <= api_version < removed:
                results[i].append(function)
    return results


def get_function_arguments(api_version, function_name):
    """Get all possible arguments for a function call
    WARNING: Doesn't check if entire function against api_version
             Only argument sets and arguments

    Arguments:
    api_version - int 
    function_name - name of function

    Return:
    array of: [ [], [a, b, c], ...]

    """
    def extract_args(a):
        """Params can be like:
        x (0)
        x, y, z
        x (0), y (0)

        """
        return [z.split()[0] for z in a.split(',')]

    data = {
        "action": "query",
        "prop": "revisions",
        "rvlimit": 1,
        "rvprop": "content",
        "format": "json",
        "titles": function_name
    }
    wiki_data = urllib.urlopen("http://www.love2d.org/w/api.php",
                               urllib.urlencode(data)).read()
    json = simplejson.loads(wiki_data)
    wikicode = mwparserfromhell.parse(
        json["query"]["pages"].values()[0]["revisions"][0]["*"])

    all_args = []

    # TODO: check if whole function was removed

    # List of == Functions ==
    sections = wikicode.get_sections(levels=[2], matches=r"(Function)")
    for section in sections:
        # Check first template in function section for newin/oldin
        try:
            f_temp = section.filter_templates()[0]
        except IndexError:
            # No templates - nothing to do
            all_args.append([])
            continue
        if f_temp.name == "newin" and api_version < int(str(f_temp.params[1])):
            # In the next version - skip to next function section
            continue
        elif f_temp.name == "oldin" and int(str(f_temp.params[1])) <= api_version:
            # Already removed - skip to next function section
            continue
        # Get the === Arguments === section templates
        arg_temps = section.get_sections(
            levels=[3],
            matches=r"(Arguments)")[0].filter_templates(recursive=False)
        args = []
        for arg_temp in arg_temps:
            name, params = arg_temp.name, arg_temp.params
            # Simple paramater
            if name == "param":
                args = args + extract_args(params[1])
            # These parameters are only available from this version
            elif name in ("New feature", "New_feature"):
                version = int(str(params[2]))
                if api_version >= version:
                    # The second param is a string...so we have to convert it
                    # to a template object, then we can get its args
                    t_args = [x.params[1] for x in
                              params[1].value.filter_templates()]
                    for t in t_args:
                        args = args + extract_args(t)
            elif name == "subparam":
                # Don't support subparams
                pass
            else:
                raise Exception("Unsupported template: %s" % name)
        all_args.append(args)
    return all_args
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.stderr.write("Usage: %s API_VERSION (ie 080)\n" % sys.argv[0])
        sys.exit(1)

    api_version = int(sys.argv[1])

    # Get data from mediawiki via Special Ask
    functions, callbacks = get_functions(api_version)

    # Loop through functions
    with open('api.txt', 'w') as api_file:
        for function in functions:
            print function
            for args in get_function_arguments(api_version, function):
                if len(args) == 0:
                    api_file.write("%s\n" % function)
                else:
                    api_file.write('%s,%s\n' % (function, ','.join(args)))

    # Loop through callbacks
    with open('callbacks.txt', 'w') as callback_file:
        for callback in callbacks:
            print callback
            for args in get_function_arguments(api_version, callback):
                if len(args) == 0:
                    callback_file.write("%s\n" % callback)
                else:
                    callback_file.write('%s,%s\n' % (callback, ','.join(args)))

