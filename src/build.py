#!/usr/bin/env python

import sys
import os
import plistlib
import json

lua_syntax = os.path.join('..', '..', 'Lua', 'Lua.tmLanguage')
syntax_out = os.path.join('..', 'Love.tmLanguage')
completions_out = os.path.join('..', 'Love.sublime-completions')

name = 'Lua (Love)'
comment = 'Lua+Love Syntax'
scopeName = 'source.lua.love'
uuid = '86A2712F-D1D2-4AB3-8788-B4A6B6215005'
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
    api_list = [line.strip() for line in fh.read().split() if line]
    fh.close()
    fh = open('callbacks.txt')
    callback_list = [line.strip() for line in fh.read().split() if line]
    fh.close()

    # Build api hierarchy
    api_dict = {}
    for line in api_list:
        namespace = api_dict
        for token in line.split('.'):
            if not namespace.get(token):
                namespace[token] = {}
            namespace = namespace[token]
    # Clone lua syntax and insert metadata
    plist = plistlib.readPlist(lua_syntax)
    plist['name'] = name
    plist['scopeName'] = scopeName
    plist['comment'] = comment
    plist['uuid'] = uuid

    # Insert love API
    lovedict = {
        'name': syntaxGroup,
        'match': r'(?<![^.]\.|:)\b%s\b(?=[( {])' % tmize(api_dict)
    }
    plist['patterns'].append(lovedict)
    plistlib.writePlist(plist, syntax_out)
    print 'Created %s' % syntax_out

    # Build completions file

    completions = []
    for line in api_list + callback_list:
        completions.append({
            'trigger': line,
            'contents': '%s($0)' % line,
        })
    fh = open(completions_out, 'w')
    json.dump({
        'scope': scopeName,
        'completions': completions,
    }, fh, sort_keys=True, indent=4)
    fh.close()
    print 'Created %s' % completions_out

if __name__ == '__main__':
    if len(sys.argv) > 1:
        lua_syntax = sys.argv[1]

    if not os.path.exists(lua_syntax):
        print 'Lua.tmLanguage not found.  Try passing it as an argument'
        sys.exit(1)

    main()
