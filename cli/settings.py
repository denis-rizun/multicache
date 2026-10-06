import argparse

from pydantic import Field, HttpUrl, PositiveInt
from pydantic_settings import BaseSettings, CliApp, CliSettingsSource, SettingsConfigDict

STDIO = "-"
PROG_NAME = "cache-cli"


class CliSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CACHE_CLI_",
        cli_prog_name=PROG_NAME,
        cli_shortcuts={"host": "h", "repeat": "r", "input": "i", "json": "j", "output": "o"},
        cli_hide_none_type=True,
    )

    host: HttpUrl = Field(HttpUrl("http://localhost:8000"), description="URL of the caching service")
    repeat: PositiveInt = Field(1, description="number of iterations")
    input: str = Field(STDIO, description=f"JSON input file ('{STDIO}' for stdin), ignored when --json is set")
    json_input: str | None = Field(None, alias="json", description="JSON input passed inline")
    output: str = Field(STDIO, description=f"output file ('{STDIO}' for stdout)")


def parse_args(args: list[str]) -> CliSettings:
    parser = argparse.ArgumentParser(prog=PROG_NAME, add_help=False)
    parser.add_argument("--help", action="help", help="show this help message and exit")
    source = CliSettingsSource[CliSettings](CliSettings, root_parser=parser)
    return CliApp.run(CliSettings, cli_args=args, cli_settings_source=source)
