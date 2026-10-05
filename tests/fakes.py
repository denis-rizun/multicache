from app.services.transformer import Transformer


class FakeTransformer(Transformer):
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def uppercase(self, value: str) -> str:
        self.calls.append(value)
        return value.upper()
