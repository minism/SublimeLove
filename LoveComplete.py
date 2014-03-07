
###
# -*- coding: utf-8 -*-

import sys

import sublime, sublime_plugin
import subprocess, time
import os


# data files
dirname = os.path.dirname(__file__)
api = os.path.join(dirname,'src','api.txt')
callbacks = os.path.join(dirname,'src','callbacks.txt')

fh = open(api)
api_list = [line.strip().split(',') for line in fh.read().split() if line]
fh.close()

fh = open(callbacks)
callbacks_list = [line.strip().split(',') for line in fh.read().split() if line]
fh.close()

# calculate library set
lib_set = []
for fn in api_list:
    fn_split = fn[0].split('.')
    lib_set.append(fn_split[1])

lib_set = list(set(lib_set))
lib_completions = []
for lib in lib_set:
    lib_completions.append(("love." + lib, "love." + lib))

# calculate callbacks

for fn in callbacks_list:
    fn_split = fn[0].split('.')
    name = fn[0]
    del fn[0]

    lib_completions.append((name + "(" + ", ".join(fn) + ")", fn_split[1] + "(" + ", ".join(fn) + ")"))


# calculate functions list
fn_completions = {}
for lib in lib_set:
    fn_completions.update({lib: []})

for fn in api_list:
    fn_split = fn[0].split('.')
    lib = fn_split[1]
    name = fn[0]
    del fn[0]

    arg_str = ""
    for i, arg in enumerate(fn):
        if i != 0:
            arg_str += ", "
        arg_str += "${" + str(i+1) + ":" + arg + "}"

    fn_completions[lib].append((name + "(" + ", ".join(fn) + ")", fn_split[2] + "(" + arg_str + ")"))


def is_love_lua(view):
    return '/Love.tmLanguage' in view.settings().get('syntax')

class LoveComplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if is_love_lua(view):
            location = locations[0]
            # this was a good way to detect libraries and stuff at the time
            # but I realized that it's not very modular or scalable
            # this whole part needs to be rethought over, but for now it works.
            lib = view.substr(view.word(location-1))
            word = view.substr(view.word(location-1).b)
            preword = view.substr(view.word(location-1-len(lib)-1).b)
            prelib = view.substr(view.word(location-1-len(lib)-1))
            prepreword = view.substr(view.word(location-1-len(lib)-1-len(prelib)-1).b)
            preprelib = view.substr(view.word(location-1-len(lib)-1-len(prelib)-1))

            if word == ".":
                if preword != "." and lib == "love":
                    return lib_completions
                elif prelib == "love" and fn_completions[lib]:
                    return fn_completions[lib]
            elif lib in "love" and preword != ".":
                return [("love", "love")]
            else:
                if preword == ".":
                    if prelib == "love":
                        ret = []
                        for completion_a, completion_b in lib_completions:
                            if lib in completion_b:
                                ret.append((completion_a, completion_b))
                        return ret
                    elif prepreword == "." and preprelib == "love" and fn_completions[prelib] and preword == ".":
                        ret = []
                        for completion_a, completion_b in fn_completions[prelib]:
                            if lib in completion_b:
                                ret.append((completion_a, completion_b))
                        return ret

