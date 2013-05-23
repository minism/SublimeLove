Description
===========

SublimeLove is a package for [Sublime Text 2](http://www.sublimetext.com/2) supporting the [Love2D](http://love2d.org) API.

Currently in alpha and still heavily a work in progress.

Installation
============

You can install this package by running the following command in your ST2 Packages directory:
    
    git clone git://github.com/minism/SublimeLove.git

Features
========

Syntax highlighting
-------------------
Hit ctrl/cmd+P, or go to View > Syntax, and set the syntax of your open file to "Lua (Love)" to enable highlighting for the Love2D API functions.  On my editor, lua files are now defaulting to this syntax, but I'm not sure how to control that.

If you create a new pixel effect, and make the argument a multi-line string, then Sublime will use C syntax highlighting for the GLSL content.

Auto completion
---------------
Pressing ctrl+space in an open Love file will show the autocompletions for the API functions.  ST2 currently has some issues with autocomplete that other plugins are also dealing with, so its not perfect yet.  One major issue is that the period key breaks tokens and doesn't get included as part of the autocomplete query.

Those Love2D functions which are not overloaded (only one possible argument combination), will fill in the argument names for you.

Build system
------------
To use the build command, the Love executable needs to be on your system PATH.  Then, go to Tools > Build System and select "Love".  Hit F7 or cmd+B to run your Love program.

The build system will automatically be selected for lua files.

Links
=====

Development
===========
Go to the **src** directory. If Love2D has been updated, run **scrape_api.py**, which generates **api.txt** and **callbacks.txt**, then run **build.py** which assembles the Sublime files.

**Love.JSON-tmLanguage** is an expanded version of the Lua syntax highlighter. Leave the **lua-love** repository entry empty, as its filled in by **build.py**
