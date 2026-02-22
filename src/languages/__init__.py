"""Language configurations for speech text conversion."""


def get_language(code: str) -> dict:
    """Return language config dict for the given language code.

    Args:
        code: Language code ('en', 'de')

    Returns:
        Language configuration dict

    Raises:
        ValueError: If language code is not supported
    """
    if code == 'en':
        from .en import LANG
        return LANG
    elif code == 'de':
        from .de import LANG
        return LANG
    else:
        raise ValueError(f"Unsupported language: {code}. Supported: en, de")
