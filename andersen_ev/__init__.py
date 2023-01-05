"""
andersen.
Python library for controlling the Andersen A2 EV car charger.
"""

# For relative imports to work in Python 3.6
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))

__version__ = "0.1.0"
__author__ = 'James Brown'
__credits__ = 'Catch22'

from .andersen import AndersenA2