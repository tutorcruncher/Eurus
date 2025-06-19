from dataclasses import dataclass

from app.utils.dataclass import BaseRequest


@dataclass
class NestedRequest(BaseRequest):
    field1: int
    field2: str


@dataclass
class ComplexRequest(BaseRequest):
    number: int
    items: list[int]
    nested: NestedRequest
    optional: str | None = None


def test_to_dict_recursive_and_none_exclusion():
    """Ensure BaseRequest.to_dict recursively serialises and omits ``None`` values."""
    nested = NestedRequest(field1=1, field2='inner')
    complex_obj = ComplexRequest(
        number=42,
        items=[1, 2, 3],
        nested=nested,
        optional=None,  # This key should be excluded
    )

    result = complex_obj.to_dict()

    # ``optional`` should not be present because it is ``None``
    assert 'optional' not in result

    assert result == {
        'number': 42,
        'items': [1, 2, 3],
        'nested': {'field1': 1, 'field2': 'inner'},
    }
