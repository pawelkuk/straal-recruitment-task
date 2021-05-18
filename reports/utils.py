def mask_card_number(card_number: str) -> str:
    return card_number[:4] + "*" * len(card_number[4:-4]) + card_number[-4:]
