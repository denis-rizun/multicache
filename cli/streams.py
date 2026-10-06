import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO

from app.schemas import PayloadCreateRequest
from cli.settings import STDIO, CliSettings


def read_request(settings: CliSettings) -> PayloadCreateRequest:
    raw = settings.json_input or read_text(settings.input)
    return PayloadCreateRequest.model_validate_json(raw)


def read_text(path: str) -> str:
    if path == STDIO:
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


@contextmanager
def open_output(path: str) -> Iterator[TextIO]:
    if path == STDIO:
        yield sys.stdout
    else:
        with open(path, "w", encoding="utf-8") as file:
            yield file
