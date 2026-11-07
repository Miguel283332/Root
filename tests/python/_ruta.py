"""Hace importables tools/ y companion/ desde los tests (sin instalar nada)."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for sub in ("tools", "companion"):
    p = str(RAIZ / sub)
    if p not in sys.path:
        sys.path.insert(0, p)
