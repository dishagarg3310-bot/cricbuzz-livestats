import json
import sys
from pathlib import Path


def show(obj, depth=0, max_depth=9):
    pad = "  " * depth
    if depth > max_depth:
        return
    if isinstance(obj, dict):
        for key, val in obj.items():
            kind = type(val).__name__
            extra = f" (len {len(val)})" if isinstance(val, (list, dict)) else ""
            print(f"{pad}{key}: {kind}{extra}")
            show(val, depth + 1, max_depth)
    elif isinstance(obj, list) and obj:
        print(f"{pad}[0] sample:")
        show(obj[0], depth + 1, max_depth)


data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
show(data)