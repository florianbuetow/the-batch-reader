"""Convert text to speech-friendly format.

This module provides functions to sanitize text for optimal text-to-speech output.
Each function handles a specific rule for text normalization.
"""

import re
import unicodedata
from typing import List


# =============================================================================
# Rule 1: Strip HTML/Markdown
# =============================================================================

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
    # Remove code blocks first (before other processing)
    text = re.sub(r'```[\s\S]*?```', '', text)

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
        '&mdash;': '—',
        '&ndash;': '–',
        '&hellip;': '…',
    }
    for entity, char in html_entities.items():
        text = text.replace(entity, char)

    # Handle numeric entities &#123;
    text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)

    return text


# =============================================================================
# Rule 2: Normalize whitespace
# =============================================================================

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.

    - Convert \\r\\n and \\r to \\n
    - Collapse runs of spaces to single spaces
    - Keep single blank line between paragraphs
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
    text = '\n'.join(lines)

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

    Handles arrows, checkmarks, math symbols, etc.
    """
    replacements = {
        # Arrows
        '→': ' arrow ',
        '←': ' arrow ',
        '↑': ' arrow ',
        '↓': ' arrow ',
        '⇒': ' implies ',
        '⇐': ' implied by ',
        '↔': ' bidirectional arrow ',

        # Checkmarks and crosses
        '✓': ' check mark ',
        '✔': ' check mark ',
        '✗': ' cross ',
        '✘': ' cross ',
        '☑': ' checked box ',
        '☐': ' unchecked box ',

        # Math symbols
        '×': ' times ',
        '÷': ' divided by ',
        '±': ' plus or minus ',
        '≈': ' approximately ',
        '≠': ' not equal to ',
        '≤': ' less than or equal to ',
        '≥': ' greater than or equal to ',
        '∞': ' infinity ',

        # Legal/copyright
        '©': ' copyright ',
        '®': ' registered trademark ',
        '™': ' trademark ',

        # Misc
        '•': ', ',
        '·': ' ',
        '…': '...',
        '§': ' section ',
        '¶': ' paragraph ',
        '†': '',
        '‡': '',
        '°': ' degrees ',
    }

    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)

    return text


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

# Number word mappings
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


def _number_to_words(n: int) -> str:
    """Convert an integer to words."""
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

    # Handle thousands, millions, billions, etc.
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


def normalize_numbers(text: str) -> str:
    """Convert numeric digits to spelled-out words.

    Examples:
    - 42 -> forty-two
    - 100 -> one hundred
    - 2025 -> twenty twenty-five (for years) or two thousand twenty-five
    """
    # Handle ordinals first (1st, 2nd, 3rd, etc.)
    for ordinal, word in ORDINALS.items():
        text = re.sub(rf'\b{ordinal}\b', word, text, flags=re.IGNORECASE)

    # Handle standalone numbers (not part of larger constructs)
    def replace_number(match):
        num_str = match.group(0)
        try:
            num = int(num_str)
            # For 4-digit numbers that look like years (1900-2099), read as two pairs
            if 1900 <= num <= 2099 and len(num_str) == 4:
                first_half = num // 100
                second_half = num % 100
                if second_half == 0:
                    return f"{_number_to_words(first_half)} hundred"
                elif second_half < 10:
                    return f"{_number_to_words(first_half)} oh {_number_to_words(second_half)}"
                else:
                    return f"{_number_to_words(first_half)} {_number_to_words(second_half)}"
            return _number_to_words(num)
        except ValueError:
            return num_str

    # Match standalone numbers (not preceded/followed by other digits or decimal points)
    text = re.sub(r'\b(\d+)\b', replace_number, text)

    return text


# =============================================================================
# Rule 6: Normalize dates
# =============================================================================

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


def normalize_dates(text: str) -> str:
    """Convert date formats to spoken form.

    Examples:
    - 10/12/2025 -> October twelve, twenty twenty-five
    - 2025-01-15 -> January fifteen, twenty twenty-five
    - 11/12/2025 -> November twelve, twenty twenty-five
    """
    def format_year(year_str: str) -> str:
        year = int(year_str)
        if 1900 <= year <= 2099:
            first_half = year // 100
            second_half = year % 100
            if second_half == 0:
                return f"{_number_to_words(first_half)} hundred"
            elif second_half < 10:
                return f"{_number_to_words(first_half)} oh {_number_to_words(second_half)}"
            else:
                return f"{_number_to_words(first_half)} {_number_to_words(second_half)}"
        return _number_to_words(year)

    def format_day(day_str: str) -> str:
        day = int(day_str)
        return _number_to_words(day)

    # MM/DD/YYYY format (US style)
    def replace_us_date(match):
        month, day, year = match.groups()
        month_name = MONTHS.get(month, month)
        return f"{month_name} {format_day(day)}, {format_year(year)}"

    text = re.sub(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', replace_us_date, text)

    # YYYY-MM-DD format (ISO style)
    def replace_iso_date(match):
        year, month, day = match.groups()
        month_name = MONTHS.get(month, month)
        return f"{month_name} {format_day(day)}, {format_year(year)}"

    text = re.sub(r'\b(\d{4})-(\d{2})-(\d{2})\b', replace_iso_date, text)

    return text


# =============================================================================
# Rule 7: Normalize symbols
# =============================================================================

def normalize_symbols(text: str) -> str:
    """Convert symbols to their spoken equivalents.

    Examples:
    - $100 -> one hundred dollars
    - 42% -> forty-two percent
    - €29.99 -> twenty-nine euros and ninety-nine cents
    - & -> and
    - + -> plus
    """
    # Currency with amounts: $100, €50, £30
    def replace_currency(match):
        symbol = match.group(1)
        amount = match.group(2)

        currency_names = {
            '$': 'dollars',
            '€': 'euros',
            '£': 'pounds',
            '¥': 'yen',
        }
        currency = currency_names.get(symbol, 'units')

        # Handle decimal amounts
        if '.' in amount:
            whole, cents = amount.split('.')
            whole_num = int(whole) if whole else 0
            cents_num = int(cents) if cents else 0

            if cents_num > 0:
                cents_word = 'cents' if symbol in ('$', '€') else 'pence' if symbol == '£' else ''
                return f"{_number_to_words(whole_num)} {currency} and {_number_to_words(cents_num)} {cents_word}".strip()
            return f"{_number_to_words(whole_num)} {currency}"

        return f"{_number_to_words(int(amount))} {currency}"

    text = re.sub(r'([$€£¥])(\d+(?:\.\d{2})?)', replace_currency, text)

    # Percentage: 42%
    def replace_percent(match):
        num = match.group(1)
        if '.' in num:
            whole, decimal = num.split('.')
            return f"{_number_to_words(int(whole))} point {' '.join(_number_to_words(int(d)) for d in decimal)} percent"
        return f"{_number_to_words(int(num))} percent"

    text = re.sub(r'(\d+(?:\.\d+)?)\s*%', replace_percent, text)

    # Time: 9:30 PM
    def replace_time(match):
        hour = int(match.group(1))
        minute = int(match.group(2))
        period = match.group(3).lower().replace('.', '') if match.group(3) else ''

        if minute == 0:
            time_str = f"{_number_to_words(hour)} o'clock"
        elif minute < 10:
            time_str = f"{_number_to_words(hour)} oh {_number_to_words(minute)}"
        else:
            time_str = f"{_number_to_words(hour)} {_number_to_words(minute)}"

        if period:
            time_str += f" {period[0]} {period[1]}"

        return time_str

    text = re.sub(r'(\d{1,2}):(\d{2})\s*(AM|PM|am|pm|a\.m\.|p\.m\.)?', replace_time, text)

    # Simple symbol replacements
    text = text.replace(' & ', ' and ')
    text = text.replace('&', ' and ')
    text = re.sub(r'(?<=[a-zA-Z])\+(?=[a-zA-Z])', ' plus ', text)  # C++ style
    text = re.sub(r'\s\+\s', ' plus ', text)  # standalone +
    text = text.replace(' = ', ' equals ')
    text = text.replace('@', ' at ')
    text = text.replace('#', ' number ')
    text = text.replace(' / ', ' slash ')

    return text


# =============================================================================
# Rule 8: Normalize acronyms
# =============================================================================

# Common acronyms that should be spelled out letter by letter
LETTER_ACRONYMS = {
    'FBI', 'CIA', 'NSA', 'USA', 'UK', 'EU', 'UN', 'NATO', 'CEO', 'CFO', 'CTO',
    'AI', 'ML', 'API', 'CPU', 'GPU', 'RAM', 'ROM', 'USB', 'HTML', 'CSS', 'URL',
    'PDF', 'FAQ', 'DIY', 'CEO', 'VP', 'HR', 'IT', 'PR', 'QA', 'R&D', 'ROI',
    'GDP', 'GPA', 'IQ', 'EQ', 'PhD', 'MBA', 'BA', 'BS', 'MS', 'MD', 'JD',
    'ASAP', 'FYI', 'BTW', 'IMO', 'TBD', 'TBA', 'ETA', 'RSVP',
    'GPS', 'ATM', 'PIN', 'ID', 'VIP', 'RSVP', 'PS', 'TV', 'DVD', 'CD',
    'LLM', 'NLP', 'GPT', 'CNN', 'RNN', 'SaaS', 'IoT', 'VR', 'AR',
}

# Acronyms that should be expanded to full words
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


def normalize_acronyms(text: str) -> str:
    """Convert acronyms to speakable form.

    Examples:
    - FBI -> F B I
    - AI -> A I
    - etc. -> et cetera
    """
    # Expand known acronyms to full words
    for abbrev, expansion in EXPANDED_ACRONYMS.items():
        # Escape any special regex chars in the abbreviation (like dots)
        escaped = re.escape(abbrev)
        # Match with optional period after (consume the period if present)
        text = re.sub(rf'\b{escaped}\.', expansion, text, flags=re.IGNORECASE)
        text = re.sub(rf'\b{escaped}\b', expansion, text, flags=re.IGNORECASE)

    # Convert letter acronyms to spaced letters
    for acronym in LETTER_ACRONYMS:
        spaced = ' '.join(acronym.upper())
        # Case insensitive match for the acronym as a whole word
        text = re.sub(rf'\b{acronym}\b', spaced, text, flags=re.IGNORECASE)

    return text


# =============================================================================
# Rule 9: Flatten lists
# =============================================================================

def flatten_lists(text: str) -> str:
    """Convert bullet/numbered lists to flowing prose.

    Transforms:
    - Bullet points (*, -, •) to numbered prose
    - Numbered lists (1., 2.) to prose
    """
    lines = text.split('\n')
    result = []
    list_items = []
    in_list = False

    for line in lines:
        # Check if line is a list item
        list_match = re.match(r'^[\s]*[-*•]\s+(.+)$', line)
        numbered_match = re.match(r'^[\s]*\d+[.)]\s+(.+)$', line)

        if list_match or numbered_match:
            in_list = True
            item = list_match.group(1) if list_match else numbered_match.group(1)
            list_items.append(item)
        else:
            # If we were in a list, convert and output it
            if in_list and list_items:
                prose = _list_to_prose(list_items)
                result.append(prose)
                list_items = []
                in_list = False
            result.append(line)

    # Handle list at end of text
    if list_items:
        prose = _list_to_prose(list_items)
        result.append(prose)

    return '\n'.join(result)


def _list_to_prose(items: List[str]) -> str:
    """Convert list items to prose format."""
    if len(items) == 1:
        return items[0]

    ordinals = ['Firstly', 'Secondly', 'Thirdly', 'Fourthly', 'Fifthly',
                'Sixthly', 'Seventhly', 'Eighthly', 'Ninthly', 'Tenthly']

    prose_parts = []
    for i, item in enumerate(items):
        if i < len(ordinals):
            prose_parts.append(f"{ordinals[i]}, {item.lower() if item[0].isupper() and not item[1:2].isupper() else item}")
        else:
            prose_parts.append(f"Additionally, {item.lower() if item[0].isupper() and not item[1:2].isupper() else item}")

    return ' '.join(prose_parts)


# =============================================================================
# Rule 10: Chunk text
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
    """Convert text to speech-friendly format.

    Applies all normalization rules in the correct order.
    """

    def __init__(self, chunk_size: int = 900):
        """Initialize converter.

        Args:
            chunk_size: Maximum characters per chunk (default 900)
        """
        self.chunk_size = chunk_size

    def convert(self, text: str) -> str:
        """Apply all normalization rules to text.

        Returns a single string with all transformations applied.
        """
        # 1. Strip markup
        text = strip_html(text)
        text = strip_markdown(text)

        # 2. Normalize whitespace
        text = normalize_whitespace(text)

        # 3. Remove dangerous punctuation
        text = remove_dangerous_punctuation(text)

        # 4. Strip control characters and weird Unicode
        text = strip_control_characters(text)
        text = remove_emojis(text)
        text = replace_special_unicode(text)

        # 5-7. Normalize dates, symbols, numbers (in this order to handle $ before numbers)
        text = normalize_dates(text)
        text = normalize_symbols(text)
        text = normalize_numbers(text)

        # 8. Normalize acronyms
        text = normalize_acronyms(text)

        # 9. Flatten lists
        text = flatten_lists(text)

        # Final whitespace cleanup
        text = normalize_whitespace(text)

        return text

    def convert_and_chunk(self, text: str) -> List[str]:
        """Apply all normalization rules and split into chunks.

        Returns a list of text chunks, each under chunk_size characters.
        """
        text = self.convert(text)
        return chunk_text(text, self.chunk_size)
