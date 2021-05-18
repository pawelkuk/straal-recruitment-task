from django.core.exceptions import ValidationError


def check_card(card_number: str) -> bool:
    """
    Credit card validation according to Luhn's algorithm
    Source: https://en.wikipedia.org/wiki/Luhn_algorithm
    """
    nums = [int(c) for c in card_number if c.isdigit()]
    checksum = nums.pop()
    nums = nums[::-1]
    doubled = [2 * n for n in nums[::2]]
    total = sum(n - 9 if n > 9 else n for n in doubled) + sum(nums[1::2])
    return (total * 9) % 10 == checksum


def card_validator(card_number: str) -> None:
    if not check_card(card_number):
        raise ValidationError("Malformed card number")
