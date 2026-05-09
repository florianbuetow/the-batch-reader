"""Convert text to speech-friendly format.

This module provides functions to sanitize text for optimal text-to-speech output.
Each function handles a specific rule for text normalization.
"""

import re
import unicodedata
from typing import List

try:
    from languages import get_language
except ImportError:
    from src.languages import get_language


# =============================================================================
# Rule 1: Strip HTML/Markdown
# =============================================================================

def remove_code_blocks(text: str, lang: dict | None = None) -> str:
    """Replace code blocks with placeholder message.

    Must be called BEFORE strip_html to prevent HTML regex from
    matching across code block boundaries (e.g., '<1ms' in text
    matching to '->' in code).
    """
    if lang is None:
        lang = get_language('en')
    return re.sub(r'```[\s\S]*?```', lang['code_block_placeholder'], text)


def strip_markdown(text: str) -> str:
    """Remove Markdown formatting from text.

    Handles:
    - Headers (# ## ###)
    - Bold (**text** or __text__)
    - Italic (*text* or _text_)
    - Links [text](url) -> text
    - Images ![alt](url) -> alt
    - Inline code `code`
    - Code blocks ```code```
    - Strikethrough ~~text~~
    - Backticks
    """
    # Note: code blocks are removed by remove_code_blocks() before this runs

    # Remove inline code
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Remove images ![alt](url) -> alt
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)

    # Remove links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Remove headers (# ## ### etc.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # Remove bold **text** or __text__
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)

    # Remove italic *text* or _text_ (careful not to match underscores in words)
    text = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'\1', text)
    text = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'\1', text)

    # Remove strikethrough ~~text~~
    text = re.sub(r'~~([^~]+)~~', r'\1', text)

    return text


def strip_html(text: str) -> str:
    """Remove HTML tags from text.

    Handles:
    - All HTML tags <tag>content</tag> -> content
    - Self-closing tags <br/>, <hr/>
    - HTML entities &amp; -> &, &lt; -> <, etc.
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Decode common HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&apos;': "'",
        '&nbsp;': ' ',
        '&#39;': "'",
        '&mdash;': '\u2014',
        '&ndash;': '\u2013',
        '&hellip;': '\u2026',
    }
    for entity, char in html_entities.items():
        text = text.replace(entity, char)

    # Handle numeric entities &#123;
    text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)

    return text


def remove_parenthetical(text: str) -> str:
    """Remove parenthetical text from text.

    Parenthetical expressions provide optional context that isn't essential
    for text-to-speech and can be distracting when read aloud.

    Examples:
    - \u03bb (lambda) -> \u03bb
    - FBI (Federal Bureau of Investigation) -> FBI
    - The value (which includes tax (12%)) -> The value

    Handles:
    - Simple parentheses
    - Nested parentheses
    - Multiple parentheses in same text
    - Cleans up extra whitespace after removal
    """
    # Remove parenthetical expressions (including nested ones)
    # This regex removes text in parentheses by matching the outermost parens
    # and everything inside them, including any nested parens
    while '(' in text:
        # Match opening paren, then anything until the matching closing paren
        # Use a simple approach: find each '(' and match to its closing ')'
        # accounting for nesting
        start = text.find('(')
        if start == -1:
            break

        # Find matching closing paren
        depth = 1
        pos = start + 1
        while pos < len(text) and depth > 0:
            if text[pos] == '(':
                depth += 1
            elif text[pos] == ')':
                depth -= 1
            pos += 1

        if depth == 0:
            # Found matching closing paren
            text = text[:start] + text[pos:]
        else:
            # Unmatched paren, just remove it
            text = text[:start] + text[start+1:]

    # Clean up extra whitespace
    # Remove multiple spaces (but preserve newlines)
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove space before punctuation
    text = re.sub(r' +([.,;:!?])', r'\1', text)
    # Clean up leading/trailing whitespace on each line
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    # Final strip
    text = text.strip()

    return text


# =============================================================================
# Rule 2: Normalize whitespace
# =============================================================================

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.

    - Convert \\r\\n and \\r to \\n
    - Collapse runs of spaces to single spaces
    - Join mid-sentence line breaks into continuous text
    - Keep blank lines as paragraph separators
    - Strip leading/trailing whitespace from lines
    """
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Replace tabs with spaces
    text = text.replace('\t', ' ')

    # Collapse multiple spaces to single space (but preserve newlines)
    text = re.sub(r'[^\S\n]+', ' ', text)

    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]

    # Join lines within paragraphs (single newlines become spaces,
    # blank lines stay as paragraph separators)
    paragraphs = []
    current = []
    for line in lines:
        if line == '':
            if current:
                paragraphs.append(' '.join(current))
                current = []
            paragraphs.append('')
        else:
            current.append(line)
    if current:
        paragraphs.append(' '.join(current))
    text = '\n'.join(paragraphs)

    # Collapse 3+ newlines to 2 (single blank line between paragraphs)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Strip leading/trailing whitespace from entire text
    text = text.strip()

    return text


# =============================================================================
# Rule 3: Remove/replace dangerous punctuation
# =============================================================================

def remove_dangerous_punctuation(text: str) -> str:
    """Remove or replace characters that harm text-to-speech quality.

    Removes: { } < > [ ]
    These characters result in low quality speech output.
    """
    # Remove curly braces
    text = text.replace('{', '').replace('}', '')

    # Remove angle brackets
    text = text.replace('<', '').replace('>', '')

    # Remove square brackets (but preserve content)
    text = re.sub(r'\[([^\]]*)\]', r'\1', text)

    return text


# =============================================================================
# Rule 4: Strip control and weird Unicode
# =============================================================================

def strip_control_characters(text: str) -> str:
    """Remove control characters except newlines.

    Removes:
    - All control characters (C0, C1) except \\n
    - Zero-width spaces and joiners
    - Non-breaking spaces (converted to regular spaces)
    - Other invisible Unicode characters
    """
    result = []
    for char in text:
        # Keep newlines
        if char == '\n':
            result.append(char)
            continue

        # Get Unicode category
        category = unicodedata.category(char)

        # Skip control characters (Cc = control, Cf = format)
        if category in ('Cc', 'Cf'):
            continue

        # Convert non-breaking space to regular space
        if char == '\u00a0':  # Non-breaking space
            result.append(' ')
            continue

        # Skip other zero-width characters
        if char in '\u200b\u200c\u200d\u2060\ufeff':
            continue

        result.append(char)

    return ''.join(result)


def replace_special_unicode(text: str) -> str:
    """Replace special Unicode symbols with word equivalents.

    Handles dashes, arrows, checkmarks, math symbols, etc.
    """
    replacements = {
        # Arrows
        '\u2192': ' arrow ',
        '\u2190': ' arrow ',
        '\u2191': ' arrow ',
        '\u2193': ' arrow ',
        '\u21d2': ' implies ',
        '\u21d0': ' implied by ',
        '\u2194': ' bidirectional arrow ',

        # Checkmarks and crosses
        '\u2713': ' check mark ',
        '\u2714': ' check mark ',
        '\u2717': ' cross ',
        '\u2718': ' cross ',
        '\u2611': ' checked box ',
        '\u2610': ' unchecked box ',

        # Math symbols
        '\u00d7': ' times ',
        '\u00f7': ' divided by ',
        '\u00b1': ' plus or minus ',
        '\u2248': ' approximately ',
        '\u2260': ' not equal to ',
        '\u2264': ' less than or equal to ',
        '\u2265': ' greater than or equal to ',
        '\u221e': ' infinity ',

        # Legal/copyright
        '\u00a9': ' copyright ',
        '\u00ae': ' registered trademark ',
        '\u2122': ' trademark ',

        # Dashes
        '\u2014': ', ',   # em dash
        '\u2013': ', ',   # en dash

        # Misc
        '\u2022': ', ',
        '\u00b7': ' ',
        '\u2026': '...',
        '\u00a7': ' section ',
        '\u00b6': ' paragraph ',
        '\u2020': '',
        '\u2021': '',
        '\u00b0': ' degrees ',
    }

    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)

    text = re.sub(r'--+', ',', text)

    return text


def capitalize_after_punctuation(text: str) -> str:
    """Capitalize the first letter after sentence-ending punctuation."""
    return re.sub(
        r'([.?!:])\s+([a-z])',
        lambda m: m.group(1) + ' ' + m.group(2).upper(),
        text,
    )


def remove_emojis(text: str) -> str:
    """Remove emoji characters from text."""
    # Remove characters in emoji Unicode ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)


# =============================================================================
# Rule 5: Normalize numbers
# =============================================================================

def normalize_numbers(text: str, lang: dict | None = None) -> str:
    """Convert numeric digits to spelled-out words.

    Examples:
    - 42 -> forty-two
    - 100 -> one hundred
    - 2025 -> twenty twenty-five (for years) or two thousand twenty-five
    """
    if lang is None:
        lang = get_language('en')
    number_to_words = lang['number_to_words']

    for ordinal, word in lang['ordinals'].items():
        text = re.sub(rf'\b{ordinal}\b', word, text, flags=re.IGNORECASE)

    def replace_number(match):
        num_str = match.group(0)
        try:
            num = int(num_str)
            # English reads years as two pairs: "twenty twenty-five"
            # German reads years as regular numbers: "zweitausendfunfundzwanzig"
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

    text = re.sub(r'\b(\d+)\b', replace_number, text)
    return text


# =============================================================================
# Rule 6: Normalize dates
# =============================================================================

def normalize_dates(text: str, lang: dict | None = None) -> str:
    """Convert date formats to spoken form.

    Examples:
    - 10/12/2025 -> October twelve, twenty twenty-five
    - 2025-01-15 -> January fifteen, twenty twenty-five
    - 11/12/2025 -> November twelve, twenty twenty-five
    """
    if lang is None:
        lang = get_language('en')
    number_to_words = lang['number_to_words']
    months = lang['months']

    def format_year(year_str: str) -> str:
        year = int(year_str)
        if not lang.get('parse_eu_dates') and 1900 <= year <= 2099:
            first_half = year // 100
            second_half = year % 100
            if second_half == 0:
                return f"{number_to_words(first_half)} hundred"
            elif second_half < 10:
                return f"{number_to_words(first_half)} oh {number_to_words(second_half)}"
            else:
                return f"{number_to_words(first_half)} {number_to_words(second_half)}"
        return number_to_words(year)

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


# =============================================================================
# Rule 7: Normalize symbols
# =============================================================================

def normalize_symbols(text: str, lang: dict | None = None) -> str:
    """Convert symbols to their spoken equivalents.

    Examples:
    - $100 -> one hundred dollars
    - 42% -> forty-two percent
    - \u20ac29.99 -> twenty-nine euros and ninety-nine cents
    - & -> and
    - + -> plus
    """
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

    text = re.sub(r'([$\u20ac\u00a3\u00a5])(\d+(?:\.\d{2})?)', replace_currency, text)

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
            # German time: "neun Uhr drei\u00dfig"
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


# =============================================================================
# Rule 8: Normalize acronyms
# =============================================================================

def normalize_acronyms(text: str, lang: dict | None = None) -> str:
    """Convert acronyms to speakable form.

    Examples:
    - FBI -> F B I
    - AI -> A I
    - etc. -> et cetera
    """
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


# =============================================================================
# Rule 9: Flatten lists
# =============================================================================

def flatten_lists(text: str, lang: dict | None = None) -> str:
    """Convert bullet/numbered lists to flowing prose.

    Transforms:
    - Bullet points (*, -, \u2022) to numbered prose
    - Numbered lists (1., 2.) to prose
    """
    if lang is None:
        lang = get_language('en')
    lines = text.split('\n')
    result = []
    list_items = []
    in_list = False

    for line in lines:
        list_match = re.match(r'^[\s]*[-*\u2022]\s+(.+)$', line)
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


# =============================================================================
# Rule 10: Flatten tables
# =============================================================================

def flatten_tables(text: str, lang: dict | None = None) -> str:
    """Convert Markdown tables to speech-friendly prose.

    Generates an intro describing the columns and row count, followed by
    each row as a sentence with column labels.

    Example input:
        | Model | Score |
        |-------|-------|
        | GPT-4 | 95 |
        | Claude | 92 |

    Example output:
        Here is a table that contains the following columns: Model and Score
        and 2 rows. I am now going to read you the rows of the table:
        Model: GPT-4. Score: 95.
        Model: Claude. Score: 92.
    """
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


def _parse_table_row(line: str) -> List[str]:
    """Parse a markdown table row into cells."""
    # Remove leading/trailing pipes and split
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]

    cells = [cell.strip() for cell in line.split('|')]
    return cells


def _format_column_list(headers: List[str], lang: dict | None = None) -> str:
    """Format column names as a natural list (a, b, and c)."""
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


def _table_row_to_prose(headers: List[str], values: List[str]) -> str:
    """Convert a table row to prose using headers as labels."""
    parts = []
    for header, value in zip(headers, values):
        if header and value:
            parts.append(f"{header}: {value}")

    return '. '.join(parts) + '.'


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


# =============================================================================
# Rule 11: Chunk text
# =============================================================================

def chunk_text(text: str, max_chars: int = 900) -> List[str]:
    """Split text into chunks at sentence boundaries.

    Args:
        text: The text to chunk
        max_chars: Maximum characters per chunk (default 900, recommended <1000)

    Returns:
        List of text chunks, each under max_chars
    """
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        sentence_len = len(sentence)

        # If single sentence is too long, split by comma or just include as-is
        if sentence_len > max_chars:
            # Flush current chunk
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_length = 0
            # Add long sentence as its own chunk
            chunks.append(sentence)
            continue

        # Check if adding this sentence would exceed limit
        # Account for space between sentences
        space_needed = 1 if current_chunk else 0

        if current_length + space_needed + sentence_len > max_chars:
            # Flush current chunk and start new one
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_len
        else:
            current_chunk.append(sentence)
            current_length += space_needed + sentence_len

    # Flush remaining
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


# =============================================================================
# Main converter class
# =============================================================================

class SpeechTextConverter:
    """Convert text to speech-friendly format."""

    def __init__(self, chunk_size: int = 900, lang: str = 'en', skip_acronyms: bool = False):
        """Initialize converter.

        Args:
            chunk_size: Maximum characters per chunk (default 900)
            lang: Language code ('en' or 'de', default 'en')
            skip_acronyms: Skip acronym normalization (default False)
        """
        self.chunk_size = chunk_size
        self.lang = get_language(lang)
        self.skip_acronyms = skip_acronyms

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
        if not self.skip_acronyms:
            text = normalize_acronyms(text, lang)
        text = flatten_lists(text, lang)
        text = flatten_tables(text, lang)
        text = normalize_whitespace(text)
        text = capitalize_after_punctuation(text)

        return text

    def convert_and_chunk(self, text: str) -> List[str]:
        """Apply all normalization rules and split into chunks."""
        text = self.convert(text)
        return chunk_text(text, self.chunk_size)


if __name__ == "__main__":
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='Convert text to speech-friendly format')
    parser.add_argument('input', help='Input text file')
    parser.add_argument('output', help='Output file path')
    parser.add_argument('--lang', default='en', choices=['en', 'de'],
                        help='Language (default: en)')
    parser.add_argument('--skip-acronyms', action='store_true',
                        help='Skip acronym normalization')
    args = parser.parse_args()
    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()
    result = SpeechTextConverter(lang=args.lang, skip_acronyms=args.skip_acronyms).convert(text)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(result)
