"""
blacklist.py

This file just contains the blacklist of the JWT tokens imported by the
app's logout resource so that tokens can be added to the blacklist when the
user logs out.
"""

BLACKLIST = set()
