import asyncio
import sys

import httpx

from cli.client import PayloadClient
from cli.runner import run
from cli.settings import CliSettings, parse_args
from cli.streams import open_output, read_request


async def send(settings: CliSettings) -> None:
    request = read_request(settings)
    with open_output(settings.output) as out:
        async with httpx.AsyncClient(base_url=str(settings.host)) as http:
            await run(PayloadClient(http), request, settings.repeat, out)


def main() -> None:
    asyncio.run(send(parse_args(sys.argv[1:])))
