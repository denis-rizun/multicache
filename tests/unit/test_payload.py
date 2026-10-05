import pytest

from app.services import transformer as transformer_module
from app.services.hash import compute_input_hash
from app.services.transformer import Transformer

pytestmark = pytest.mark.unit


class TestComputeInputHash:
    def test_is_stable_for_the_same_input(self) -> None:
        assert compute_input_hash(["a", "b"], ["x", "y"]) == compute_input_hash(["a", "b"], ["x", "y"])

    def test_depends_on_the_order_of_values(self) -> None:
        assert compute_input_hash(["a", "b"], ["x", "y"]) != compute_input_hash(["b", "a"], ["x", "y"])

    def test_depends_on_which_list_holds_a_value(self) -> None:
        assert compute_input_hash(["a"], ["x"]) != compute_input_hash(["x"], ["a"])

    def test_does_not_collide_on_values_containing_separators(self) -> None:
        assert compute_input_hash(["a,b"], ["c"]) != compute_input_hash(["a"], ["b,c"])


class TestTransformer:
    async def test_uppercases_the_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(transformer_module, "TRANSFORM_DELAY_SECONDS", 0)

        assert await Transformer().uppercase("Hello") == "HELLO"
