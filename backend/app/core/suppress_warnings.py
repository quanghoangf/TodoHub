"""Suppress known compatibility warnings."""

import logging
import warnings

# Suppress bcrypt version compatibility warnings
# This is a known issue between newer bcrypt versions and passlib
# that doesn't affect functionality
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Also suppress any bcrypt-related warnings
warnings.filterwarnings("ignore", message=".*bcrypt.*")
warnings.filterwarnings("ignore", message=".*trapped.*")