"""
ma.py

This file imports Marshmallow from Flask to allow Marshmallow
to integrate with Flask by initializing it within our app.
"""

from flask_marshmallow import Marshmallow

ma = Marshmallow()
