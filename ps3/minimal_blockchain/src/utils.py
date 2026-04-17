import json
import hashlib
from pathlib import Path


def encode_for_hashing(x):
    """
    Deterministic JSON encoding required by the assignment.
    """
    return json.dumps(
        x,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def sha256_of_json(obj) -> str:
    return sha256_bytes(encode_for_hashing(obj))