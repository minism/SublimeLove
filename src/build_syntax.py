#!/usr/bin/env python


#
import sys
import os
import plistlib

lua_syntax = '../../Lua/Lua.tmLanguage'
out_file = '../Love.tmLanguage'

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
    # Build api hierarchy
    fh = open('api.txt')
    love_api = {}
    for line in (line.strip() for line in fh.read().split() if line):
        namespace = love_api
        for token in line.split('.'):
            if not namespace.get(token):
                namespace[token] = {}
            namespace = namespace[token]
    fh.close()

    # Clone lua syntax and insert metadata
    plist = plistlib.readPlist(lua_syntax)
    plist['name'] = name
    plist['scopeName'] = scopeName
    plist['comment'] = comment
    plist['uuid'] = uuid

    # Insert love API
    lovedict = {
        'name': syntaxGroup,
        'match': r'(?<![^.]\.|:)\b%s\b(?=[( {])' % tmize(love_api)
    }
    plist['patterns'].append(lovedict)
    plistlib.writePlist(plist, out_file)
    print 'Created %s' % out_file

if __name__ == '__main__':
    if len(sys.argv) > 1:
        lua_syntax = sys.argv[1]

    if not os.path.exists(lua_syntax):
        print 'Lua syntax file not found.  Try passing it as an argument'
        sys.exit(1)

    main()
