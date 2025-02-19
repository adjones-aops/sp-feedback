# bootstrap.py
import os
import sys

# Add the repository root (one level up from streamlit_app) to the PYTHONPATH.
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
