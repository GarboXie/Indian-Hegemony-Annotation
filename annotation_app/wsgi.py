"""WSGI entry point for the independent Taiwan deployment."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app import app as application
