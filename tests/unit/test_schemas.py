import pytest
from pydantic import ValidationError

from app.schemas import PayloadCreateRequest

pytestmark = pytest.mark.unit


class TestPayloadCreateRequest:
    def test_accepts_lists_of_equal_length(self) -> None:
        request = PayloadCreateRequest(list_1=["a", "b"], list_2=["x", "y"])

        assert (request.list_1, request.list_2) == (["a", "b"], ["x", "y"])

    def test_rejects_lists_of_different_length(self) -> None:
        with pytest.raises(ValidationError, match="list_1 and list_2 must have same length"):
            PayloadCreateRequest(list_1=["a", "b"], list_2=["x"])

    @pytest.mark.parametrize(("list_1", "list_2"), [([], ["x"]), (["a"], []), ([], [])])
    def test_rejects_an_empty_list(self, list_1: list[str], list_2: list[str]) -> None:
        with pytest.raises(ValidationError):
            PayloadCreateRequest(list_1=list_1, list_2=list_2)
