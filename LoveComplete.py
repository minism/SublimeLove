
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




class LoveComplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if '.lua' in view.file_name():
            location = locations[0]
            word = view.substr(location-1)
            lib = view.substr(view.word(location-1))
            preword = view.substr(location-1-len(lib)-1)
            prelib = view.substr(view.word(location-1-len(lib)-1))

            if word == ".":
                if preword != ".":
                    if lib == "love":
                        return lib_completions
                        # completions = list(set([
                        #     ("love.graphics", "love.graphics")
                        # ]))
                        # return completions
                elif prelib == "love":
                    if fn_completions[lib]:
                        return fn_completions[lib]
                    # if lib == "graphics":
                    #     return fn_completions
                        # completions = list(set([
                        #     ("love.graphics.printf()", "printf(${1:text}, ${2:x}, ${3:y}, ${4:limit}, ${5:align})"),
                        #     ("love.graphics.setColor(r, g, b, a)", "setColor(${1:number r}, ${2:number g}, ${3:number b})")
                        # ]))
                        # return completions
