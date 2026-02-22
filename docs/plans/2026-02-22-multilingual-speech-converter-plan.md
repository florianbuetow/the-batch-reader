# Multilingual Speech Text Converter Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add German language support to `SpeechTextConverter` via explicit `lang` flag so one-off German text files can be cleaned for TTS.

**Architecture:** Language-sensitive functions receive a lang config dict. Each language is a module in `src/languages/` exporting a dict with number words, months, templates, acronyms, and a `number_to_words` callable. English remains the default; all existing tests pass unchanged.

**Tech Stack:** Python, pytest. No new dependencies.

---

### Task 1: Create English language module

Extract all English-specific constants from `src/speech_text.py` into `src/languages/en.py` and create the `src/languages/__init__.py` registry.

**Files:**
- Create: `src/languages/__init__.py`
- Create: `src/languages/en.py`

**Step 1: Create `src/languages/__init__.py`**

```python
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
        from languages.en import LANG
        return LANG
    elif code == 'de':
        from languages.de import LANG
        return LANG
    else:
        raise ValueError(f"Unsupported language: {code}. Supported: en, de")
```

**Step 2: Create `src/languages/en.py`**

Move the following constants from `src/speech_text.py` into this file: `ONES`, `TENS`, `SCALES`, `ORDINALS`, `MONTHS`, `LETTER_ACRONYMS`, `EXPANDED_ACRONYMS`, and the `_number_to_words` function.

```python
"""English language configuration for speech text conversion."""

ONES = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
        'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
        'seventeen', 'eighteen', 'nineteen']
TENS = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
SCALES = ['', 'thousand', 'million', 'billion', 'trillion']

ORDINALS = {
    '1st': 'first', '2nd': 'second', '3rd': 'third', '4th': 'fourth',
    '5th': 'fifth', '6th': 'sixth', '7th': 'seventh', '8th': 'eighth',
    '9th': 'ninth', '10th': 'tenth', '11th': 'eleventh', '12th': 'twelfth',
    '13th': 'thirteenth', '14th': 'fourteenth', '15th': 'fifteenth',
    '16th': 'sixteenth', '17th': 'seventeenth', '18th': 'eighteenth',
    '19th': 'nineteenth', '20th': 'twentieth', '21st': 'twenty-first',
    '22nd': 'twenty-second', '23rd': 'twenty-third', '24th': 'twenty-fourth',
    '25th': 'twenty-fifth', '26th': 'twenty-sixth', '27th': 'twenty-seventh',
    '28th': 'twenty-eighth', '29th': 'twenty-ninth', '30th': 'thirtieth',
    '31st': 'thirty-first',
}

MONTHS = {
    '01': 'January', '1': 'January',
    '02': 'February', '2': 'February',
    '03': 'March', '3': 'March',
    '04': 'April', '4': 'April',
    '05': 'May', '5': 'May',
    '06': 'June', '6': 'June',
    '07': 'July', '7': 'July',
    '08': 'August', '8': 'August',
    '09': 'September', '9': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December',
}

LETTER_ACRONYMS = {
    'FBI', 'CIA', 'NSA', 'USA', 'UK', 'EU', 'UN', 'NATO', 'CEO', 'CFO', 'CTO',
    'AI', 'ML', 'API', 'CPU', 'GPU', 'RAM', 'ROM', 'USB', 'HTML', 'CSS', 'URL',
    'PDF', 'FAQ', 'DIY', 'CEO', 'VP', 'HR', 'IT', 'PR', 'QA', 'R&D', 'ROI',
    'GDP', 'GPA', 'IQ', 'EQ', 'PhD', 'MBA', 'BA', 'BS', 'MS', 'MD', 'JD',
    'ASAP', 'FYI', 'BTW', 'IMO', 'TBD', 'TBA', 'ETA', 'RSVP',
    'GPS', 'ATM', 'PIN', 'ID', 'VIP', 'RSVP', 'PS', 'TV', 'DVD', 'CD',
    'LLM', 'NLP', 'GPT', 'CNN', 'RNN', 'SaaS', 'IoT', 'VR', 'AR',
}

EXPANDED_ACRONYMS = {
    'etc': 'et cetera',
    'vs': 'versus',
    'ie': 'that is',
    'i.e': 'that is',
    'eg': 'for example',
    'e.g': 'for example',
    'approx': 'approximately',
    'govt': 'government',
    'dept': 'department',
    'inc': 'incorporated',
    'corp': 'corporation',
    'ltd': 'limited',
    'assn': 'association',
    'intl': 'international',
}


def _number_to_words(n: int) -> str:
    """Convert an integer to English words."""
    if n == 0:
        return 'zero'
    if n < 0:
        return 'negative ' + _number_to_words(-n)
    if n < 20:
        return ONES[n]
    if n < 100:
        tens, ones = divmod(n, 10)
        if ones:
            return f"{TENS[tens]}-{ONES[ones]}"
        return TENS[tens]
    if n < 1000:
        hundreds, remainder = divmod(n, 100)
        if remainder:
            return f"{ONES[hundreds]} hundred {_number_to_words(remainder)}"
        return f"{ONES[hundreds]} hundred"
    parts = []
    scale_idx = 0
    while n > 0:
        n, chunk = divmod(n, 1000)
        if chunk:
            chunk_words = _number_to_words(chunk)
            if scale_idx > 0:
                parts.append(f"{chunk_words} {SCALES[scale_idx]}")
            else:
                parts.append(chunk_words)
        scale_idx += 1
    return ' '.join(reversed(parts))


LANG = {
    'number_to_words': _number_to_words,
    'ordinals': ORDINALS,
    'months': MONTHS,
    'letter_acronyms': LETTER_ACRONYMS,
    'expanded_acronyms': EXPANDED_ACRONYMS,
    'parse_eu_dates': False,
    'currency_names': {'$': 'dollars', '€': 'euros', '£': 'pounds', '¥': 'yen'},
    'currency_subunit': {'$': 'cents', '€': 'cents', '£': 'pence'},
    'symbol_replacements': [
        (' & ', ' and '),
        ('&', ' and '),
        (' = ', ' equals '),
        ('@', ' at '),
        ('#', ' number '),
        (' / ', ' slash '),
    ],
    'percent_word': 'percent',
    'point_word': 'point',
    'oclock': "o'clock",
    'list_ordinals': ['Firstly', 'Secondly', 'Thirdly', 'Fourthly', 'Fifthly',
                      'Sixthly', 'Seventhly', 'Eighthly', 'Ninthly', 'Tenthly'],
    'list_overflow': 'Additionally',
    'and_word': 'and',
    'table_intro': "Here is a table that contains the following columns: {columns} and {count} {row_word}. I am now going to read you the rows of the table:",
    'table_row_singular': 'row',
    'table_row_plural': 'rows',
    'code_block_placeholder': 'Skipping code block.',
}
```

**Step 3: Run existing tests to verify nothing breaks yet**

Run: `make test`
Expected: All tests PASS (language modules are created but not yet used by speech_text.py)

**Step 4: Commit**

```bash
git add src/languages/__init__.py src/languages/en.py
git commit -m "Extract English language data into language module"
```

---

### Task 2: Add German language module (TDD)

Create `src/languages/de.py` with German number-to-words function and all German language data. Write tests first.

**Files:**
- Create: `tests/test_speech_text_de.py`
- Create: `src/languages/de.py`

**Step 1: Write failing tests for German number-to-words**

```python
"""Tests for German speech text conversion."""

import pytest
from src.languages.de import _number_to_words_de


class TestGermanNumberToWords:
    """Tests for German number-to-words conversion."""

    def test_zero(self):
        assert _number_to_words_de(0) == 'null'

    def test_one_standalone(self):
        assert _number_to_words_de(1) == 'eins'

    def test_small_numbers(self):
        assert _number_to_words_de(2) == 'zwei'
        assert _number_to_words_de(5) == 'fünf'
        assert _number_to_words_de(12) == 'zwölf'
        assert _number_to_words_de(16) == 'sechzehn'
        assert _number_to_words_de(17) == 'siebzehn'

    def test_tens(self):
        assert _number_to_words_de(20) == 'zwanzig'
        assert _number_to_words_de(30) == 'dreißig'
        assert _number_to_words_de(70) == 'siebzig'

    def test_compound_numbers_ones_before_tens(self):
        """German puts ones before tens: 21 = einundzwanzig (one-and-twenty)."""
        assert _number_to_words_de(21) == 'einundzwanzig'
        assert _number_to_words_de(42) == 'zweiundvierzig'
        assert _number_to_words_de(99) == 'neunundneunzig'

    def test_hundreds(self):
        assert _number_to_words_de(100) == 'einhundert'
        assert _number_to_words_de(200) == 'zweihundert'
        assert _number_to_words_de(342) == 'dreihundertzweiundvierzig'

    def test_thousands(self):
        assert _number_to_words_de(1000) == 'eintausend'
        assert _number_to_words_de(2025) == 'zweitausendfünfundzwanzig'
        assert _number_to_words_de(1999) == 'eintausendneunhundertneunundneunzig'

    def test_millions(self):
        assert _number_to_words_de(1000000) == 'eine Million'
        assert _number_to_words_de(2000000) == 'zwei Millionen'

    def test_negative(self):
        assert _number_to_words_de(-5) == 'minus fünf'
```

**Step 2: Run tests to verify they fail**

Run: `make test`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.languages.de'`

**Step 3: Create `src/languages/de.py`**

```python
"""German language configuration for speech text conversion."""

ONES_DE = ['', 'eins', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben', 'acht', 'neun',
           'zehn', 'elf', 'zwölf', 'dreizehn', 'vierzehn', 'fünfzehn', 'sechzehn',
           'siebzehn', 'achtzehn', 'neunzehn']

# 'ein' instead of 'eins' when used inside compounds (einhundert, einundzwanzig)
ONES_COMPOUND_DE = ['', 'ein', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben', 'acht', 'neun',
                    'zehn', 'elf', 'zwölf', 'dreizehn', 'vierzehn', 'fünfzehn', 'sechzehn',
                    'siebzehn', 'achtzehn', 'neunzehn']

TENS_DE = ['', '', 'zwanzig', 'dreißig', 'vierzig', 'fünfzig', 'sechzig', 'siebzig', 'achtzig', 'neunzig']

MONTHS_DE = {
    '01': 'Januar', '1': 'Januar',
    '02': 'Februar', '2': 'Februar',
    '03': 'März', '3': 'März',
    '04': 'April', '4': 'April',
    '05': 'Mai', '5': 'Mai',
    '06': 'Juni', '6': 'Juni',
    '07': 'Juli', '7': 'Juli',
    '08': 'August', '8': 'August',
    '09': 'September', '9': 'September',
    '10': 'Oktober',
    '11': 'November',
    '12': 'Dezember',
}

# German letter acronyms - same international set plus German-specific ones
LETTER_ACRONYMS_DE = {
    'FBI', 'CIA', 'NSA', 'USA', 'UK', 'EU', 'UN', 'NATO', 'CEO', 'CFO', 'CTO',
    'AI', 'ML', 'API', 'CPU', 'GPU', 'RAM', 'ROM', 'USB', 'HTML', 'CSS', 'URL',
    'PDF', 'FAQ', 'DIY', 'CEO', 'VP', 'HR', 'IT', 'PR', 'QA', 'ROI',
    'GDP', 'IQ', 'EQ', 'PhD', 'MBA',
    'ASAP', 'FYI', 'TBD', 'TBA', 'ETA', 'RSVP',
    'GPS', 'ATM', 'PIN', 'ID', 'VIP', 'PS', 'TV', 'DVD', 'CD',
    'LLM', 'NLP', 'GPT', 'CNN', 'RNN', 'SaaS', 'IoT', 'VR', 'AR',
    'GmbH', 'AG', 'EZB', 'BIP', 'TÜV', 'ADAC',
}

EXPANDED_ACRONYMS_DE = {
    'etc': 'et cetera',
    'vs': 'versus',
    'bzw': 'beziehungsweise',
    'z.B': 'zum Beispiel',
    'd.h': 'das heißt',
    'usw': 'und so weiter',
    'ggf': 'gegebenenfalls',
    'ca': 'circa',
    'evtl': 'eventuell',
    'inkl': 'inklusive',
    'exkl': 'exklusive',
}


def _number_to_words_de(n: int) -> str:
    """Convert an integer to German words."""
    if n == 0:
        return 'null'
    if n < 0:
        return 'minus ' + _number_to_words_de(-n)
    return _ntw_de(n, compound=False)


def _ntw_de(n: int, compound: bool = True) -> str:
    """Inner German number-to-words. compound=True uses 'ein' instead of 'eins'."""
    ones = ONES_COMPOUND_DE if compound else ONES_DE

    if n < 20:
        return ones[n]

    if n < 100:
        tens_digit, ones_digit = divmod(n, 10)
        if ones_digit:
            return f"{ONES_COMPOUND_DE[ones_digit]}und{TENS_DE[tens_digit]}"
        return TENS_DE[tens_digit]

    if n < 1000:
        hundreds, remainder = divmod(n, 100)
        result = f"{ONES_COMPOUND_DE[hundreds]}hundert"
        if remainder:
            result += _ntw_de(remainder)
        return result

    if n < 1000000:
        thousands, remainder = divmod(n, 1000)
        if thousands == 1:
            result = "eintausend"
        else:
            result = f"{_ntw_de(thousands)}tausend"
        if remainder:
            result += _ntw_de(remainder)
        return result

    if n < 1000000000:
        millions, remainder = divmod(n, 1000000)
        if millions == 1:
            result = "eine Million"
        else:
            result = f"{_ntw_de(millions)} Millionen"
        if remainder:
            result += " " + _ntw_de(remainder)
        return result

    billions, remainder = divmod(n, 1000000000)
    if billions == 1:
        result = "eine Milliarde"
    else:
        result = f"{_ntw_de(billions)} Milliarden"
    if remainder:
        result += " " + _ntw_de(remainder)
    return result


LANG = {
    'number_to_words': _number_to_words_de,
    'ordinals': {},  # German ordinals ("1.") are too ambiguous with sentence-ending dots
    'months': MONTHS_DE,
    'letter_acronyms': LETTER_ACRONYMS_DE,
    'expanded_acronyms': EXPANDED_ACRONYMS_DE,
    'parse_eu_dates': True,  # DD.MM.YYYY instead of MM/DD/YYYY
    'currency_names': {'$': 'Dollar', '€': 'Euro', '£': 'Pfund', '¥': 'Yen'},
    'currency_subunit': {'$': 'Cent', '€': 'Cent', '£': 'Pence'},
    'symbol_replacements': [
        (' & ', ' und '),
        ('&', ' und '),
        (' = ', ' gleich '),
        ('@', ' at '),
        ('#', ' Nummer '),
        (' / ', ' Schrägstrich '),
    ],
    'percent_word': 'Prozent',
    'point_word': 'Komma',
    'oclock': 'Uhr',
    'list_ordinals': ['Erstens', 'Zweitens', 'Drittens', 'Viertens', 'Fünftens',
                      'Sechstens', 'Siebtens', 'Achtens', 'Neuntens', 'Zehntens'],
    'list_overflow': 'Außerdem',
    'and_word': 'und',
    'table_intro': "Hier ist eine Tabelle mit den Spalten: {columns} und {count} {row_word}. Ich lese jetzt die Zeilen vor:",
    'table_row_singular': 'Zeile',
    'table_row_plural': 'Zeilen',
    'code_block_placeholder': 'Codeblock wird übersprungen.',
}
```

**Step 4: Run tests to verify German number tests pass**

Run: `make test`
Expected: All tests PASS (existing English + new German number tests)

**Step 5: Commit**

```bash
git add src/languages/de.py tests/test_speech_text_de.py
git commit -m "Add German language module with number-to-words"
```

---

### Task 3: Refactor speech_text.py to use language configs

Change every language-sensitive function to accept an optional `lang` parameter (defaults to English). Remove moved constants. Existing tests must pass unchanged.

**Files:**
- Modify: `src/speech_text.py`

**Step 1: Remove moved constants and add lang import**

At the top of `src/speech_text.py`, remove all of these (lines 339-617):
- `ONES`, `TENS`, `SCALES` (lines 340-344)
- `ORDINALS` (lines 346-357)
- `_number_to_words()` function (lines 360-397)
- `MONTHS` (lines 441-454)
- `LETTER_ACRONYMS` (lines 591-599)
- `EXPANDED_ACRONYMS` (lines 602-617)

Add this import at the top (after existing imports):

```python
from languages import get_language
```

**Step 2: Refactor `remove_code_blocks`**

```python
def remove_code_blocks(text: str, lang: dict | None = None) -> str:
    """Replace code blocks with placeholder message."""
    if lang is None:
        lang = get_language('en')
    return re.sub(r'```[\s\S]*?```', lang['code_block_placeholder'], text)
```

**Step 3: Refactor `normalize_numbers`**

```python
def normalize_numbers(text: str, lang: dict | None = None) -> str:
    """Convert numeric digits to spelled-out words."""
    if lang is None:
        lang = get_language('en')
    number_to_words = lang['number_to_words']

    for ordinal, word in lang['ordinals'].items():
        text = re.sub(rf'\b{ordinal}\b', word, text, flags=re.IGNORECASE)

    def replace_number(match):
        num_str = match.group(0)
        try:
            num = int(num_str)
            if 1900 <= num <= 2099 and len(num_str) == 4:
                first_half = num // 100
                second_half = num % 100
                if second_half == 0:
                    return f"{number_to_words(first_half)} hundred"
                elif second_half < 10:
                    return f"{number_to_words(first_half)} oh {number_to_words(second_half)}"
                else:
                    return f"{number_to_words(first_half)} {number_to_words(second_half)}"
            return number_to_words(num)
        except ValueError:
            return num_str

    text = re.sub(r'\b(\d+)\b', replace_number, text)
    return text
```

Note: The year-reading logic ("twenty twenty-five") is English-specific. For German, years go through `number_to_words` directly which produces "zweitausendfünfundzwanzig" - the standard German form. So we should condition the year-splitting on NOT being a language that handles years naturally:

```python
    def replace_number(match):
        num_str = match.group(0)
        try:
            num = int(num_str)
            # English reads years as two pairs: "twenty twenty-five"
            # German reads years as regular numbers: "zweitausendfünfundzwanzig"
            if not lang.get('parse_eu_dates') and 1900 <= num <= 2099 and len(num_str) == 4:
                first_half = num // 100
                second_half = num % 100
                if second_half == 0:
                    return f"{number_to_words(first_half)} hundred"
                elif second_half < 10:
                    return f"{number_to_words(first_half)} oh {number_to_words(second_half)}"
                else:
                    return f"{number_to_words(first_half)} {number_to_words(second_half)}"
            return number_to_words(num)
        except ValueError:
            return num_str
```

**Step 4: Refactor `normalize_dates`**

```python
def normalize_dates(text: str, lang: dict | None = None) -> str:
    """Convert date formats to spoken form."""
    if lang is None:
        lang = get_language('en')
    number_to_words = lang['number_to_words']
    months = lang['months']

    def format_year(year_str: str) -> str:
        return number_to_words(int(year_str))

    def format_day(day_str: str) -> str:
        return number_to_words(int(day_str))

    if lang.get('parse_eu_dates'):
        # DD.MM.YYYY format (European style)
        def replace_eu_date(match):
            day, month, year = match.groups()
            month_name = months.get(month.lstrip('0'), month)
            return f"{format_day(day)} {month_name}, {format_year(year)}"
        text = re.sub(r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b', replace_eu_date, text)
    else:
        # MM/DD/YYYY format (US style)
        def replace_us_date(match):
            month, day, year = match.groups()
            month_name = months.get(month, month)
            return f"{month_name} {format_day(day)}, {format_year(year)}"
        text = re.sub(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', replace_us_date, text)

    # YYYY-MM-DD format (ISO style) - both languages
    def replace_iso_date(match):
        year, month, day = match.groups()
        month_name = months.get(month, month)
        return f"{month_name} {format_day(day)}, {format_year(year)}"
    text = re.sub(r'\b(\d{4})-(\d{2})-(\d{2})\b', replace_iso_date, text)

    return text
```

**Step 5: Refactor `normalize_symbols`**

```python
def normalize_symbols(text: str, lang: dict | None = None) -> str:
    """Convert symbols to their spoken equivalents."""
    if lang is None:
        lang = get_language('en')
    number_to_words = lang['number_to_words']

    def replace_currency(match):
        symbol = match.group(1)
        amount = match.group(2)
        currency = lang['currency_names'].get(symbol, 'units')
        if '.' in amount:
            whole, cents = amount.split('.')
            whole_num = int(whole) if whole else 0
            cents_num = int(cents) if cents else 0
            if cents_num > 0:
                cents_word = lang['currency_subunit'].get(symbol, '')
                return f"{number_to_words(whole_num)} {currency} {lang['and_word']} {number_to_words(cents_num)} {cents_word}".strip()
            return f"{number_to_words(whole_num)} {currency}"
        return f"{number_to_words(int(amount))} {currency}"

    text = re.sub(r'([$€£¥])(\d+(?:\.\d{2})?)', replace_currency, text)

    def replace_percent(match):
        num = match.group(1)
        if '.' in num:
            whole, decimal = num.split('.')
            return f"{number_to_words(int(whole))} {lang['point_word']} {' '.join(number_to_words(int(d)) for d in decimal)} {lang['percent_word']}"
        return f"{number_to_words(int(num))} {lang['percent_word']}"

    text = re.sub(r'(\d+(?:\.\d+)?)\s*%', replace_percent, text)

    def replace_time(match):
        hour = int(match.group(1))
        minute = int(match.group(2))
        period = match.group(3).lower().replace('.', '') if match.group(3) else ''

        if lang.get('parse_eu_dates'):
            # German time: "neun Uhr dreißig"
            if minute == 0:
                time_str = f"{number_to_words(hour)} {lang['oclock']}"
            else:
                time_str = f"{number_to_words(hour)} {lang['oclock']} {number_to_words(minute)}"
        else:
            # English time: "nine thirty p m"
            if minute == 0:
                time_str = f"{number_to_words(hour)} {lang['oclock']}"
            elif minute < 10:
                time_str = f"{number_to_words(hour)} oh {number_to_words(minute)}"
            else:
                time_str = f"{number_to_words(hour)} {number_to_words(minute)}"

            if period:
                time_str += f" {period[0]} {period[1]}"

        return time_str

    text = re.sub(r'(\d{1,2}):(\d{2})\s*(AM|PM|am|pm|a\.m\.|p\.m\.)?', replace_time, text)

    # Configurable symbol replacements
    for old, new in lang['symbol_replacements']:
        text = text.replace(old, new)

    # Plus handling (same in both languages)
    text = re.sub(r'(?<=[a-zA-Z])\+(?=[a-zA-Z])', ' plus ', text)
    text = re.sub(r'\s\+\s', ' plus ', text)

    return text
```

**Step 6: Refactor `normalize_acronyms`**

```python
def normalize_acronyms(text: str, lang: dict | None = None) -> str:
    """Convert acronyms to speakable form."""
    if lang is None:
        lang = get_language('en')

    for abbrev, expansion in lang['expanded_acronyms'].items():
        escaped = re.escape(abbrev)
        text = re.sub(rf'\b{escaped}\.', expansion, text, flags=re.IGNORECASE)
        text = re.sub(rf'\b{escaped}\b', expansion, text, flags=re.IGNORECASE)

    for acronym in lang['letter_acronyms']:
        spaced = ' '.join(acronym.upper())
        text = re.sub(rf'\b{acronym}\b(?!\')', spaced, text)

    return text
```

**Step 7: Refactor `flatten_lists` and `_list_to_prose`**

```python
def flatten_lists(text: str, lang: dict | None = None) -> str:
    """Convert bullet/numbered lists to flowing prose."""
    if lang is None:
        lang = get_language('en')
    lines = text.split('\n')
    result = []
    list_items = []
    in_list = False

    for line in lines:
        list_match = re.match(r'^[\s]*[-*•]\s+(.+)$', line)
        numbered_match = re.match(r'^[\s]*\d+[.)]\s+(.+)$', line)

        if list_match or numbered_match:
            in_list = True
            item = list_match.group(1) if list_match else numbered_match.group(1)
            list_items.append(item)
        else:
            if in_list and list_items:
                prose = _list_to_prose(list_items, lang)
                result.append(prose)
                list_items = []
                in_list = False
            result.append(line)

    if list_items:
        prose = _list_to_prose(list_items, lang)
        result.append(prose)

    return '\n'.join(result)


def _list_to_prose(items: List[str], lang: dict | None = None) -> str:
    """Convert list items to prose format."""
    if lang is None:
        lang = get_language('en')
    if len(items) == 1:
        return items[0]

    ordinals = lang['list_ordinals']
    overflow = lang['list_overflow']

    prose_parts = []
    for i, item in enumerate(items):
        if i < len(ordinals):
            prose_parts.append(f"{ordinals[i]}, {item.lower() if item[0].isupper() and not item[1:2].isupper() else item}")
        else:
            prose_parts.append(f"{overflow}, {item.lower() if item[0].isupper() and not item[1:2].isupper() else item}")

    return ' '.join(prose_parts)
```

**Step 8: Refactor `flatten_tables`, `_format_column_list`, and `_table_to_prose`**

```python
def flatten_tables(text: str, lang: dict | None = None) -> str:
    """Convert Markdown tables to speech-friendly prose."""
    if lang is None:
        lang = get_language('en')
    lines = text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if '|' in line and i + 1 < len(lines):
            next_line = lines[i + 1]
            if re.match(r'^[\s]*\|[\s\-:|]+\|[\s]*$', next_line):
                headers = _parse_table_row(line)
                if headers:
                    i += 2
                    data_rows = []
                    while i < len(lines) and '|' in lines[i]:
                        row_line = lines[i]
                        if re.match(r'^[\s]*\|[\s\-:|]+\|[\s]*$', row_line):
                            break
                        values = _parse_table_row(row_line)
                        if values:
                            data_rows.append(values)
                        i += 1
                    table_prose = _table_to_prose(headers, data_rows, lang)
                    result.append(table_prose)
                    continue
        result.append(line)
        i += 1

    return '\n'.join(result)


def _format_column_list(headers: List[str], lang: dict | None = None) -> str:
    """Format column names as a natural list."""
    if lang is None:
        lang = get_language('en')
    headers = [h for h in headers if h]
    if len(headers) == 0:
        return ""
    if len(headers) == 1:
        return headers[0]
    and_word = lang['and_word']
    if len(headers) == 2:
        return f"{headers[0]} {and_word} {headers[1]}"
    return ', '.join(headers[:-1]) + f', {and_word} {headers[-1]}'


def _table_to_prose(headers: List[str], data_rows: List[List[str]], lang: dict | None = None) -> str:
    """Convert a full table to prose with intro and rows."""
    if lang is None:
        lang = get_language('en')
    row_count = len(data_rows)
    row_word = lang['table_row_singular'] if row_count == 1 else lang['table_row_plural']
    column_list = _format_column_list(headers, lang)
    intro = lang['table_intro'].format(columns=column_list, count=row_count, row_word=row_word)
    row_lines = [_table_row_to_prose(headers, values) for values in data_rows]
    return intro + '\n' + '\n'.join(row_lines)
```

**Step 9: Update `SpeechTextConverter` class**

```python
class SpeechTextConverter:
    """Convert text to speech-friendly format."""

    def __init__(self, chunk_size: int = 900, lang: str = 'en'):
        """Initialize converter.

        Args:
            chunk_size: Maximum characters per chunk (default 900)
            lang: Language code ('en' or 'de', default 'en')
        """
        self.chunk_size = chunk_size
        self.lang = get_language(lang)

    def convert(self, text: str) -> str:
        """Apply all normalization rules to text."""
        lang = self.lang

        text = remove_code_blocks(text, lang)
        text = strip_html(text)
        text = strip_markdown(text)
        text = remove_parenthetical(text)
        text = normalize_whitespace(text)
        text = remove_dangerous_punctuation(text)
        text = strip_control_characters(text)
        text = remove_emojis(text)
        text = replace_special_unicode(text)
        text = normalize_dates(text, lang)
        text = normalize_symbols(text, lang)
        text = normalize_numbers(text, lang)
        text = normalize_acronyms(text, lang)
        text = flatten_lists(text, lang)
        text = flatten_tables(text, lang)
        text = normalize_whitespace(text)

        return text

    def convert_and_chunk(self, text: str) -> List[str]:
        """Apply all normalization rules and split into chunks."""
        text = self.convert(text)
        return chunk_text(text, self.chunk_size)
```

**Step 10: Update `__main__` block**

```python
if __name__ == "__main__":
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='Convert text to speech-friendly format')
    parser.add_argument('--lang', default='en', choices=['en', 'de'],
                        help='Language (default: en)')
    args = parser.parse_args()
    text = sys.stdin.read()
    print(SpeechTextConverter(lang=args.lang).convert(text))
```

**Step 11: Run ALL existing English tests**

Run: `make test`
Expected: ALL tests PASS. Every existing test calls functions without `lang` param, which defaults to English. Zero test changes needed.

**Step 12: Commit**

```bash
git add src/speech_text.py
git commit -m "Refactor speech text converter to use language configs"
```

---

### Task 4: Add German conversion tests

Write tests for German dates, symbols, acronyms, lists, tables, and full converter integration.

**Files:**
- Modify: `tests/test_speech_text_de.py`

**Step 1: Add German conversion tests**

Append to `tests/test_speech_text_de.py`:

```python
from src.speech_text import (
    normalize_numbers,
    normalize_dates,
    normalize_symbols,
    normalize_acronyms,
    flatten_lists,
    flatten_tables,
    remove_code_blocks,
    SpeechTextConverter,
)
from src.languages import get_language

DE = get_language('de')


class TestGermanNormalizeNumbers:
    def test_small_number(self):
        assert normalize_numbers("Ich habe 42 Äpfel", DE) == "Ich habe zweiundvierzig Äpfel"

    def test_year_as_regular_number(self):
        """German reads years as regular numbers, not split pairs."""
        assert normalize_numbers("Im Jahr 2025", DE) == "Im Jahr zweitausendfünfundzwanzig"

    def test_zero(self):
        assert normalize_numbers("Er hat 0 Punkte", DE) == "Er hat null Punkte"

    def test_hundred(self):
        assert normalize_numbers("Es gibt 100 Teilnehmer", DE) == "Es gibt einhundert Teilnehmer"


class TestGermanNormalizeDates:
    def test_eu_date_format(self):
        """DD.MM.YYYY -> day month_name, year_words."""
        result = normalize_dates("Am 12.10.2025", DE)
        assert "zwölf" in result
        assert "Oktober" in result
        assert "zweitausendfünfundzwanzig" in result

    def test_iso_date(self):
        result = normalize_dates("Datum: 2025-01-15", DE)
        assert "Januar" in result
        assert "fünfzehn" in result

    def test_does_not_parse_us_dates(self):
        """German should not parse MM/DD/YYYY."""
        result = normalize_dates("On 10/12/2025", DE)
        assert "Oktober" not in result  # Not parsed as US date


class TestGermanNormalizeSymbols:
    def test_dollar(self):
        result = normalize_symbols("Kosten: $100", DE)
        assert "einhundert Dollar" in result

    def test_euro(self):
        result = normalize_symbols("Preis: €50", DE)
        assert "fünfzig Euro" in result

    def test_percent(self):
        assert "zweiundvierzig Prozent" in normalize_symbols("wuchs um 42%", DE)

    def test_ampersand(self):
        assert normalize_symbols("Forschung & Entwicklung", DE) == "Forschung und Entwicklung"

    def test_time(self):
        result = normalize_symbols("um 9:30", DE)
        assert "neun" in result
        assert "Uhr" in result
        assert "dreißig" in result


class TestGermanNormalizeAcronyms:
    def test_letter_acronyms(self):
        assert normalize_acronyms("Die AI revolutioniert", DE) == "Die A I revolutioniert"

    def test_german_expansions(self):
        assert "beziehungsweise" in normalize_acronyms("bzw.", DE)
        assert "zum Beispiel" in normalize_acronyms("z.B.", DE)
        assert "das heißt" in normalize_acronyms("d.h.", DE)
        assert "und so weiter" in normalize_acronyms("usw.", DE)


class TestGermanFlattenLists:
    def test_bullet_list(self):
        result = flatten_lists("Punkte:\n- Erster Punkt\n- Zweiter Punkt\n- Dritter Punkt", DE)
        assert "Erstens" in result
        assert "Zweitens" in result
        assert "Drittens" in result


class TestGermanFlattenTables:
    def test_simple_table(self):
        input_text = """| Name | Alter |
|------|-------|
| Alice | 30 |
| Bob | 25 |"""
        result = flatten_tables(input_text, DE)
        assert "Hier ist eine Tabelle" in result
        assert "und" in result
        assert "2 Zeilen" in result
        assert "|" not in result


class TestGermanCodeBlocks:
    def test_german_placeholder(self):
        result = remove_code_blocks("Vor\n```python\nprint('hello')\n```\nNach", DE)
        assert "Codeblock wird übersprungen" in result


class TestGermanSpeechTextConverter:
    def test_full_german_conversion(self):
        converter = SpeechTextConverter(lang='de')
        result = converter.convert("Am 12.10.2025 wuchs der Umsatz um 42%.")
        assert "Oktober" in result
        assert "zweiundvierzig Prozent" in result
        assert "%" not in result

    def test_german_default_unchanged(self):
        """English converter still works as default."""
        converter = SpeechTextConverter()
        result = converter.convert("In 2025, growth was 42%.")
        assert "twenty twenty-five" in result
        assert "forty-two percent" in result
```

**Step 2: Run all tests**

Run: `make test`
Expected: ALL tests PASS (existing English + new German)

**Step 3: Commit**

```bash
git add tests/test_speech_text_de.py
git commit -m "Add German conversion tests for dates, symbols, lists, tables"
```

---

### Task 5: CLI integration

Add `--lang` flag to `fetch_article.py` and `LANG=` param to Makefile.

**Files:**
- Modify: `src/fetch_article.py`
- Modify: `Makefile`

**Step 1: Update `src/fetch_article.py`**

Add `--lang` argument to argparse (after the `-o` argument, around line 168):

```python
    parser.add_argument(
        '-l', '--lang',
        default='en',
        choices=['en', 'de'],
        help='Language for speech conversion (default: en)'
    )
```

Update `fetch_and_convert` signature to accept `lang` parameter:

```python
def fetch_and_convert(url: str, output_dir: Path, lang: str = 'en') -> Path:
```

Change the converter instantiation (line 132) from:

```python
    converter = SpeechTextConverter()
```

To:

```python
    converter = SpeechTextConverter(lang=lang)
```

Update the call in `main()` (line 177) from:

```python
    output_path = fetch_and_convert(args.url, output_dir)
```

To:

```python
    output_path = fetch_and_convert(args.url, output_dir, lang=args.lang)
```

**Step 2: Update `Makefile` fetch target**

Change the fetch target (lines 40-49) to pass LANG:

```makefile
fetch:
	@echo ""
ifndef URL
	@echo "Error: URL parameter required"
	@echo "Usage: make fetch URL=https://example.com/article"
	@echo ""
	@exit 1
endif
ifdef LANG
	@uv run src/fetch_article.py "$(URL)" --lang "$(LANG)"
else
	@uv run src/fetch_article.py "$(URL)"
endif
	@echo ""
```

Also update the `convert` target to pass LANG:

```makefile
convert:
ifdef LANG
	@uv run src/speech_text.py --lang "$(LANG)"
else
	@uv run src/speech_text.py
endif
```

And update the help text:

```makefile
	@echo "  fetch      Fetch and convert a URL (use: make fetch URL=... [LANG=de])"
```

**Step 3: Run tests and manual verify**

Run: `make test`
Expected: ALL tests PASS

Manual test: `echo "Am 12.10.2025 wuchs der Umsatz um 42%." | make convert LANG=de`
Expected: Output contains "Oktober", "zweiundvierzig Prozent"

**Step 4: Commit**

```bash
git add src/fetch_article.py Makefile
git commit -m "Add --lang flag to fetch and convert commands"
```
