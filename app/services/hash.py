import hashlib
import json


def hash_string(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def compute_input_hash(list_1: list[str], list_2: list[str]) -> str:
    canonical = json.dumps([list_1, list_2], ensure_ascii=False, separators=(",", ":"))
    return hash_string(canonical)
