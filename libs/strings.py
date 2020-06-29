"""
libs.string

Uses 'en-us.json' to populate error strings within the API.
To change the language, set 'libs.strings.default_locale'
and then run 'libs.strings.refresh()
"""

import json

default_locale = "en-us"
cached_strings = {}


# Refreshes what language's strings are being loaded for error messages.
def refresh():
    global cached_strings
    with open(f"strings/{default_locale}.json") as f:
        cached_strings = json.load(f)


# Retrieves a particular string from the locale.
def gettext(name):
    return cached_strings[name]


refresh()
