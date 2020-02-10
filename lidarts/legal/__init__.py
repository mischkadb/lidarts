# -*- coding: utf-8 -*-

"""Legal Blueprint initialization.

Includes disclaimer, privacy notice, imprint, T&C etc.
"""

from flask import Blueprint


bp = Blueprint('legal', __name__)

from lidarts.legal import routes  # noqa F401
