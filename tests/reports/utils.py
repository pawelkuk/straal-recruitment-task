import pytest

from reports.utils import mask_card_number


@pytest.mark.parametrize(
    "input_card,masked_card",
    [
        ("341111111111111", "3411*******1111"),
        ("378282246310005", "3782*******0005"),
        ("111111111111111111", "1111**********1111"),
        ("111111111", "1111*1111"),
    ],
)
def test_mask_card_number_masks_correctly(input_card, masked_card):
    assert mask_card_number(input_card) == masked_card
