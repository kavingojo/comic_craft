import sys
from pathlib import Path

# Ensure project root and app directory are in sys.path
_app_dir = Path(__file__).resolve().parent
_project_root = _app_dir.parent
for _p in (str(_project_root), str(_app_dir), r"C:\RASH", r"C:\RASH\comiccraft"):
    if _p not in sys.path:
        sys.path.insert(0, _p)
