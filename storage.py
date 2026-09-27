import json
import os
import sys


def _base_dir():
    # When frozen by PyInstaller, __file__ points inside a temporary extraction
    # folder that's wiped after the program exits, so we save next to the .exe
    # itself instead, to persist across runs.
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


SAVE_PATH = os.path.join(_base_dir(), "save.json")


def load():
    if not os.path.exists(SAVE_PATH):
        return None
    try:
        with open(SAVE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return None


def save(data):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump(data, f)
    except Exception:
        pass