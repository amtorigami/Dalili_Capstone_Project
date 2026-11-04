import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE_DIR = BASE / "mock_api"
LANDING_DIR = BASE.parent / "data" / "landing"


def file_hash(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def run():
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nouveaux, inchanges = 0, 0

    for src in sorted(SOURCE_DIR.glob("*.json")):
        json.loads(src.read_text(encoding="utf-8"))

        dest_dir = LANDING_DIR / src.stem
        dest_dir.mkdir(parents=True, exist_ok=True)

        landed = sorted(dest_dir.glob("*.json"))
        if landed and file_hash(landed[-1]) == file_hash(src):
            inchanges += 1
            continue

        shutil.copy2(src, dest_dir / f"{run_ts}.json")
        nouveaux += 1

    print(f"run {run_ts} : {nouveaux} nouveau(x) fichier(s), {inchanges} inchangé(s)")


if __name__ == "__main__":
    run()