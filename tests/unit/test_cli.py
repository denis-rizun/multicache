import io
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from cli.settings import parse_args
from cli.streams import read_request

pytestmark = pytest.mark.unit

REQUEST = {"list_1": ["a", "b"], "list_2": ["x", "y"]}
REQUEST_JSON = json.dumps(REQUEST)


class TestParseArgs:
    def test_applies_defaults(self) -> None:
        settings = parse_args([])

        assert (str(settings.host), settings.repeat, settings.input, settings.output) == (
            "http://localhost:8000/",
            1,
            "-",
            "-",
        )

    def test_accepts_short_flags(self) -> None:
        settings = parse_args(["-h", "http://api:9000", "-r", "3", "-i", "in.json", "-j", "{}", "-o", "out.jsonl"])

        assert (str(settings.host), settings.repeat, settings.input, settings.json_input, settings.output) == (
            "http://api:9000/",
            3,
            "in.json",
            "{}",
            "out.jsonl",
        )

    @pytest.mark.parametrize("args", [["--repeat", "0"], ["--repeat", "x"], ["--host", "not a url"]])
    def test_rejects_invalid_arguments(self, args: list[str]) -> None:
        with pytest.raises(ValidationError):
            parse_args(args)


class TestReadRequest:
    def test_reads_inline_json(self) -> None:
        assert read_request(parse_args(["--json", REQUEST_JSON])).model_dump() == REQUEST

    def test_reads_a_file(self, tmp_path: Path) -> None:
        path = tmp_path / "input.json"
        path.write_text(REQUEST_JSON)

        assert read_request(parse_args(["--input", str(path)])).model_dump() == REQUEST

    def test_reads_stdin_by_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("sys.stdin", io.StringIO(REQUEST_JSON))

        assert read_request(parse_args([])).model_dump() == REQUEST

    @pytest.mark.parametrize("raw", ["not json", '{"list_1": ["a"], "list_2": ["x", "y"]}'])
    def test_rejects_an_invalid_request(self, raw: str) -> None:
        with pytest.raises(ValidationError):
            read_request(parse_args(["--json", raw]))
