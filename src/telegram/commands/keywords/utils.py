import re
from typing import List


def parse_keywords(text: str) -> List[str]:
    """
    Split and normalize a string by commas or spaces.
    """
    return [k.strip().lower() for k in re.split(r"[, ]+", text) if k.strip()]
