"""
api/index.py — Serverless function entrypoint for Vercel.
Exposes the ASGI app directly to Vercel's Python runtime.
"""

import sys
import os

# Add root directory to sys.path so main, service, db, etc. resolve correctly
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import db
from main import app

# Ensure database tables and initial reviewer seed exist
db.init()
