import pytest

from reports.validators import check_card


@pytest.mark.parametrize(
    "input_card,expected_output",
    [
        ("341111111111111", True),
        ("378282246310005", True),
        ("111111111111111111", False),
        ("111111111", False),
        ("371449635398431", True),
        ("6011000990139424", True),
        ("6011000990139425", False),
    ],
)
def test_card_validator_returns_correct_anwsers(input_card, expected_output):
    assert check_card(input_card) == expected_output
