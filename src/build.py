#!/usr/bin/env python

import sys
import os
import plistlib
import simplejson

lua_syntax = os.path.join('..', 'Love.JSON-tmLanguage')
syntax_out = os.path.join('..', 'Love.tmLanguage')
completions_out = os.path.join('..', 'Love.sublime-completions')
scopeName = 'source.lua.love'
syntaxGroup = 'support.function.library.lua.love'


def tmize(node):
    assert(isinstance(node, dict))
    buf = []
    for key, val in node.items():
        if len(val.keys()) == 0:
            buf.append(key)
        else:
            buf.append('%s\.%s' % (key, tmize(val)))
    return '(%s)' % '|'.join(buf)


def main():
    # Parse api
    fh = open('api.txt')
    api_list = [line.strip().split(',') for line in fh.read().split() if line]
    fh.close()
    fh = open('callbacks.txt')
    callback_list = [line.strip().split(',') for line in fh.read().split() if line]
    fh.close()

    # Build api hierarchy
    api_dict = {}
    for line in api_list:
        namespace = api_dict
        api_call = line[0]
        for token in api_call.split('.'):
            if not namespace.get(token):
                namespace[token] = {}
            namespace = namespace[token]
    # Clone lua syntax
    lua = simplejson.load(open(lua_syntax, 'r'))

    # Insert love API
    love_match = r'(?<![^.]\.|:)\b%s\b(?=[( {])' % tmize(api_dict)
    lua['repository']['lua-love']["match"] = love_match
    plistlib.writePlist(lua, syntax_out)
    print 'Created %s' % syntax_out

    # Filter unique arguments
    api_args = {}
    for line in api_list + callback_list:
        api_call = line[0]
        if api_call not in api_args:
            api_args[api_call] = line[1:]
        else:
            # We don't know how to nicely handle overloading
            api_args[api_call] = []

    # Build completions file
    completions = []
    for call, args in api_args.iteritems():
        arguments = ["${%s:%s}" % (i + 1, arg) for (i, arg) in enumerate(args)]
        completions.append({
            'trigger': call,
            'contents': '%s(%s)' % (call, ', '.join(arguments) if len(arguments) != 0 else "$0"),
        })
    fh = open(completions_out, 'w')
    simplejson.dump({
        'scope': scopeName,
        'completions': completions,
    }, fh, sort_keys=True, indent=4)
    fh.close()
    print 'Created %s' % completions_out

if __name__ == '__main__':
    main()
