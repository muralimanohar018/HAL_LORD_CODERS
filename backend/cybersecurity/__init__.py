"""
CampusShield cybersecurity verification package.
"""

from .campusshield_engine import analyze_message
from .risk_aggregator import analyze_security

__all__ = ["analyze_message", "analyze_security"]
