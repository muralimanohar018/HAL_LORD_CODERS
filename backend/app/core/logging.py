"""Logging setup module.

Responsibility:
- Centralize logger initialization for the backend app.
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """Create or retrieve a configured logger."""
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)
