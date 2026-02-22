"""Pytest configuration for the governance engine tests."""
import sys
import os

# Ensure src/ is on the path so `ghoststack` package resolves
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
