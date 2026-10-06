import asyncio

TRANSFORM_DELAY_SECONDS = 1.0


class Transformer:
    """Mock of an external transformation service"""

    async def uppercase(self, value: str) -> str:
        await asyncio.sleep(TRANSFORM_DELAY_SECONDS)
        return value.upper()
