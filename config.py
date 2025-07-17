def str_to_bool(s: str) -> bool:
    """
    Convert a string to a boolean.

    Returns True if the string (case-insensitive) matches common truthy values:
    'true', '1', 'yes', 'y', or 'on'. Otherwise, returns False.
    """

    return s.lower() in ("true", "1", "yes", "y", "on")
