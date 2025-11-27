"""Tests for speech text conversion functions.

Each test uses examples from text-to-speech best practices.
"""

import pytest
from src.speech_text import (
    strip_markdown,
    strip_html,
    normalize_whitespace,
    remove_dangerous_punctuation,
    strip_control_characters,
    replace_special_unicode,
    remove_emojis,
    normalize_numbers,
    normalize_dates,
    normalize_symbols,
    normalize_acronyms,
    flatten_lists,
    chunk_text,
    SpeechTextConverter,
)


# =============================================================================
# Rule 1: Strip HTML/Markdown
# =============================================================================

class TestStripMarkdown:
    """Tests for strip_markdown function."""

    def test_removes_headers(self):
        """Remove markdown headers (# ## ###)."""
        assert strip_markdown("# Header") == "Header"
        assert strip_markdown("## Second Header") == "Second Header"
        assert strip_markdown("### Third Header") == "Third Header"

    def test_removes_bold(self):
        """Remove bold markers **text** and __text__."""
        assert strip_markdown("This is **bold** text") == "This is bold text"
        assert strip_markdown("This is __bold__ text") == "This is bold text"

    def test_removes_italic(self):
        """Remove italic markers *text* and _text_."""
        assert strip_markdown("This is *italic* text") == "This is italic text"
        assert strip_markdown("This is _italic_ text") == "This is italic text"

    def test_removes_links_keeps_text(self):
        """Remove links [text](url) -> text."""
        input_text = "See [this link](https://example.com) for details"
        expected = "See this link for details"
        assert strip_markdown(input_text) == expected

    def test_removes_images(self):
        """Remove images ![alt](url) -> alt."""
        input_text = "An image: ![my image](https://example.com/img.png)"
        expected = "An image: my image"
        assert strip_markdown(input_text) == expected

    def test_removes_inline_code(self):
        """Remove inline code backticks `code`."""
        # Example from docs: Remove backticks `like this`
        assert strip_markdown("Use `code` here") == "Use code here"

    def test_removes_code_blocks(self):
        """Remove code blocks ```code```."""
        input_text = "Before\n```python\nprint('hello')\n```\nAfter"
        expected = "Before\n\nAfter"
        assert strip_markdown(input_text) == expected

    def test_removes_strikethrough(self):
        """Remove strikethrough ~~text~~."""
        assert strip_markdown("This is ~~deleted~~ text") == "This is deleted text"


class TestStripHtml:
    """Tests for strip_html function."""

    def test_removes_simple_tags(self):
        """Remove HTML tags and keep content."""
        assert strip_html("<p>Hello</p>") == "Hello"
        assert strip_html("<strong>bold</strong>") == "bold"

    def test_removes_self_closing_tags(self):
        """Remove self-closing tags like <br/>."""
        assert strip_html("Line one<br/>Line two") == "Line oneLine two"

    def test_decodes_html_entities(self):
        """Decode HTML entities."""
        assert strip_html("&amp;") == "&"
        assert strip_html("&lt;") == "<"
        assert strip_html("&gt;") == ">"
        assert strip_html("&quot;") == '"'
        assert strip_html("&nbsp;") == " "

    def test_decodes_numeric_entities(self):
        """Decode numeric HTML entities."""
        assert strip_html("&#39;") == "'"
        assert strip_html("&#65;") == "A"


# =============================================================================
# Rule 2: Normalize whitespace
# =============================================================================

class TestNormalizeWhitespace:
    """Tests for normalize_whitespace function."""

    def test_converts_line_endings(self):
        """Convert \\r\\n and \\r to \\n."""
        assert normalize_whitespace("line1\r\nline2") == "line1\nline2"
        assert normalize_whitespace("line1\rline2") == "line1\nline2"

    def test_collapses_multiple_spaces(self):
        """Collapse runs of spaces to single space."""
        assert normalize_whitespace("too   many    spaces") == "too many spaces"

    def test_collapses_multiple_newlines(self):
        """Keep single blank line between paragraphs (collapse 3+ to 2)."""
        input_text = "para1\n\n\n\npara2"
        expected = "para1\n\npara2"
        assert normalize_whitespace(input_text) == expected

    def test_strips_line_whitespace(self):
        """Strip leading/trailing whitespace from lines."""
        input_text = "  line1  \n  line2  "
        expected = "line1\nline2"
        assert normalize_whitespace(input_text) == expected

    def test_replaces_tabs(self):
        """Replace tabs with spaces."""
        assert normalize_whitespace("word1\tword2") == "word1 word2"


# =============================================================================
# Rule 3: Remove/replace dangerous punctuation
# =============================================================================

class TestRemoveDangerousPunctuation:
    """Tests for remove_dangerous_punctuation function.

    Non textual-like characters and punctuation such as
    {,},<,>,[,] will usually result in low quality speech.
    """

    def test_removes_curly_braces(self):
        """Remove { } characters."""
        # Example from docs: avoid { }
        assert remove_dangerous_punctuation("function{body}") == "functionbody"

    def test_removes_angle_brackets(self):
        """Remove < > characters."""
        # Example from docs: avoid < >
        assert remove_dangerous_punctuation("see <important> note") == "see important note"

    def test_removes_square_brackets_keeps_content(self):
        """Remove [ ] but keep content inside."""
        # Example from docs: [Note] -> Note
        assert remove_dangerous_punctuation("[Note] See section") == "Note See section"
        assert remove_dangerous_punctuation("footnote [2010]") == "footnote 2010"

    def test_complex_example(self):
        """Test complex example from docs."""
        # Example from user's text: "[Note] See §3.2 for details <important>"
        input_text = "[Note] See details <important>"
        expected = "Note See details important"
        assert remove_dangerous_punctuation(input_text) == expected


# =============================================================================
# Rule 4: Strip control and weird Unicode
# =============================================================================

class TestStripControlCharacters:
    """Tests for strip_control_characters function."""

    def test_keeps_newlines(self):
        """Preserve newline characters."""
        assert strip_control_characters("line1\nline2") == "line1\nline2"

    def test_removes_control_chars(self):
        """Remove control characters."""
        assert strip_control_characters("text\x00here") == "texthere"
        assert strip_control_characters("text\x1fhere") == "texthere"

    def test_converts_nbsp(self):
        """Convert non-breaking space to regular space."""
        assert strip_control_characters("word\u00a0word") == "word word"

    def test_removes_zero_width(self):
        """Remove zero-width spaces and joiners."""
        assert strip_control_characters("word\u200bword") == "wordword"
        assert strip_control_characters("word\u200cword") == "wordword"
        assert strip_control_characters("word\ufeffword") == "wordword"


class TestReplaceSpecialUnicode:
    """Tests for replace_special_unicode function."""

    def test_replaces_arrows(self):
        """Replace arrow symbols with words."""
        # Example from docs: → -> arrow
        assert "arrow" in replace_special_unicode("→")

    def test_replaces_checkmarks(self):
        """Replace checkmarks with words."""
        # Example from docs: ✓ -> check mark
        assert "check mark" in replace_special_unicode("✓")

    def test_replaces_copyright(self):
        """Replace copyright symbol."""
        # Example from docs: © -> copyright
        assert "copyright" in replace_special_unicode("©")

    def test_replaces_section_symbol(self):
        """Replace section symbol."""
        # Example from docs: § -> section
        assert replace_special_unicode("See §3.2") == "See  section 3.2"

    def test_replaces_degrees(self):
        """Replace degree symbol."""
        assert "degrees" in replace_special_unicode("90°")


class TestRemoveEmojis:
    """Tests for remove_emojis function."""

    def test_removes_common_emojis(self):
        """Remove emoji characters."""
        # Example from docs: emojis tend to confuse the AI
        assert remove_emojis("Hello 😀 World") == "Hello  World"
        assert remove_emojis("Great 🚀 launch") == "Great  launch"

    def test_preserves_regular_text(self):
        """Preserve regular text without emojis."""
        assert remove_emojis("Hello World") == "Hello World"


# =============================================================================
# Rule 5: Normalize numbers
# =============================================================================

class TestNormalizeNumbers:
    """Tests for normalize_numbers function."""

    def test_small_numbers(self):
        """Convert small numbers to words."""
        # Example from docs: 42 -> forty-two
        assert normalize_numbers("I have 42 apples") == "I have forty-two apples"

    def test_hundred(self):
        """Convert hundreds to words."""
        # Example from docs: 100 -> one hundred
        assert normalize_numbers("I have 100 items") == "I have one hundred items"

    def test_year_format(self):
        """Convert years to spoken format."""
        # Example from docs: 2025 -> twenty twenty-five
        assert normalize_numbers("In 2025") == "In twenty twenty-five"
        assert normalize_numbers("In 2000") == "In twenty hundred"
        assert normalize_numbers("In 1999") == "In nineteen ninety-nine"

    def test_ordinals(self):
        """Convert ordinal numbers."""
        # Example from docs: 21st -> twenty-first
        assert normalize_numbers("the 21st century") == "the twenty-first century"
        assert normalize_numbers("on the 1st") == "on the first"
        assert normalize_numbers("the 2nd place") == "the second place"
        assert normalize_numbers("the 3rd option") == "the third option"

    def test_zero(self):
        """Convert zero."""
        assert normalize_numbers("I have 0 items") == "I have zero items"

    def test_large_numbers(self):
        """Convert large numbers."""
        assert "one thousand" in normalize_numbers("1000 people")
        assert "one million" in normalize_numbers("1000000 dollars")


# =============================================================================
# Rule 6: Normalize dates
# =============================================================================

class TestNormalizeDates:
    """Tests for normalize_dates function."""

    def test_us_date_format(self):
        """Convert MM/DD/YYYY format."""
        # Example from docs: 10/12/2025 -> October twelve, twenty twenty-five
        result = normalize_dates("On 10/12/2025")
        assert "October" in result
        assert "twelve" in result
        assert "twenty twenty-five" in result

    def test_november_date(self):
        """Convert November date."""
        # Example from docs: 11/12/2025 -> November twelve
        result = normalize_dates("Date: 11/12/2025")
        assert "November" in result
        assert "twelve" in result

    def test_iso_date_format(self):
        """Convert YYYY-MM-DD format."""
        result = normalize_dates("On 2025-01-15")
        assert "January" in result
        assert "fifteen" in result


# =============================================================================
# Rule 7: Normalize symbols
# =============================================================================

class TestNormalizeSymbols:
    """Tests for normalize_symbols function."""

    def test_dollar_amounts(self):
        """Convert dollar amounts."""
        # Example from docs: $100 -> one hundred dollars
        assert normalize_symbols("Cost: $100") == "Cost: one hundred dollars"

    def test_dollar_with_cents(self):
        """Convert dollar amounts with cents."""
        # Example from docs: $42.50 -> forty-two dollars and fifty cents
        result = normalize_symbols("Price: $42.50")
        assert "forty-two dollars" in result
        assert "fifty cents" in result

    def test_euro_amounts(self):
        """Convert euro amounts."""
        # Example from docs: €29.99 -> twenty-nine euros and ninety-nine cents
        result = normalize_symbols("Price: €29.99")
        assert "twenty-nine euros" in result
        assert "ninety-nine cents" in result

    def test_percentage(self):
        """Convert percentages."""
        # Example from docs: % -> percent
        assert normalize_symbols("grew by 42%") == "grew by forty-two percent"

    def test_ampersand(self):
        """Convert ampersand."""
        # Example from docs: & -> and
        assert normalize_symbols("R & D") == "R and D"
        assert normalize_symbols("R&D") == "R and D"

    def test_plus(self):
        """Convert plus sign."""
        # Example from docs: + -> plus
        assert normalize_symbols("2 + 2") == "2 plus 2"

    def test_time_format(self):
        """Convert time format."""
        # Example from docs: 9:30 PM -> nine thirty p m
        result = normalize_symbols("at 9:30 PM")
        assert "nine" in result
        assert "thirty" in result
        assert "p m" in result


# =============================================================================
# Rule 8: Normalize acronyms
# =============================================================================

class TestNormalizeAcronyms:
    """Tests for normalize_acronyms function."""

    def test_letter_acronyms(self):
        """Convert acronyms to spaced letters."""
        # Example from docs: FBI -> F B I
        assert normalize_acronyms("The FBI investigated") == "The F B I investigated"
        assert normalize_acronyms("Use AI for this") == "Use A I for this"

    def test_expanded_acronyms(self):
        """Expand common abbreviations."""
        # Example from docs: etc. -> et cetera
        assert normalize_acronyms("and so on, etc.") == "and so on, et cetera"
        assert normalize_acronyms("us vs them") == "us versus them"
        assert normalize_acronyms("i.e. this") == "that is this"
        assert normalize_acronyms("e.g. example") == "for example example"

    def test_tech_acronyms(self):
        """Convert tech acronyms."""
        assert normalize_acronyms("The API endpoint") == "The A P I endpoint"
        assert normalize_acronyms("Train the LLM") == "Train the L L M"

    def test_it_pronoun_not_converted(self):
        """Ensure 'it' (lowercase pronoun) is not converted to 'I T'."""
        assert normalize_acronyms("it works well") == "it works well"
        assert normalize_acronyms("use it for this") == "use it for this"
        assert normalize_acronyms("I find it helpful") == "I find it helpful"

    def test_it_possessive_not_converted(self):
        """Ensure "IT's" (possessive/contraction) is not converted to "I T's"."""
        assert normalize_acronyms("IT's sometimes faster") == "IT's sometimes faster"
        assert normalize_acronyms("it's a good idea") == "it's a good idea"

    def test_it_acronym_converted(self):
        """Ensure 'IT' (Information Technology) is converted when standalone."""
        assert normalize_acronyms("The IT department") == "The I T department"
        assert normalize_acronyms("work in IT") == "work in I T"


# =============================================================================
# Rule 9: Flatten lists
# =============================================================================

class TestFlattenLists:
    """Tests for flatten_lists function."""

    def test_bullet_list_dash(self):
        """Convert dash bullet lists to prose."""
        input_text = "Items:\n- First item\n- Second item\n- Third item"
        result = flatten_lists(input_text)
        assert "Firstly" in result
        assert "Secondly" in result
        assert "Thirdly" in result

    def test_bullet_list_asterisk(self):
        """Convert asterisk bullet lists to prose."""
        input_text = "Items:\n* First item\n* Second item"
        result = flatten_lists(input_text)
        assert "Firstly" in result
        assert "Secondly" in result

    def test_numbered_list(self):
        """Convert numbered lists to prose."""
        input_text = "Steps:\n1. Do this\n2. Do that"
        result = flatten_lists(input_text)
        assert "Firstly" in result
        assert "Secondly" in result

    def test_single_item(self):
        """Single item list returns just the item."""
        input_text = "Item:\n- Only one"
        result = flatten_lists(input_text)
        assert "Only one" in result

    def test_preserves_non_list(self):
        """Preserve text that isn't a list."""
        input_text = "This is normal text."
        assert flatten_lists(input_text) == input_text


# =============================================================================
# Rule 10: Chunk text
# =============================================================================

class TestChunkText:
    """Tests for chunk_text function."""

    def test_short_text_single_chunk(self):
        """Short text returns single chunk."""
        text = "This is short."
        chunks = chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_respects_max_chars(self):
        """All chunks under max_chars limit."""
        # Create long text
        text = "This is a sentence. " * 100
        chunks = chunk_text(text, max_chars=200)
        for chunk in chunks:
            assert len(chunk) <= 200

    def test_splits_at_sentence_boundary(self):
        """Splits at sentence boundaries when possible."""
        text = "First sentence. Second sentence. Third sentence."
        chunks = chunk_text(text, max_chars=30)
        # Each chunk should end with proper punctuation
        for chunk in chunks:
            assert chunk.rstrip().endswith('.') or len(chunk) < 30

    def test_short_text_stays_together(self):
        """Short text stays in one chunk."""
        text = "Para one. Para two."
        chunks = chunk_text(text, max_chars=1000)
        assert len(chunks) == 1


# =============================================================================
# Integration: Full converter
# =============================================================================

class TestSpeechTextConverter:
    """Tests for the full SpeechTextConverter class."""

    def test_full_example(self):
        """Test a full text-to-speech conversion example.

        Raw text:
        > In 2025, revenue grew by 42%.
        > Source: [https://example.com/report](https://example.com/report).
        > [Note] See §3.2 for details <important>.

        Expected (prepared for text-to-speech):
        > In twenty-twenty-five, revenue grew by forty-two percent.
        > Source: example dot com slash report.
        > Note: see section three point two for details, important.
        """
        input_text = """In 2025, revenue grew by 42%.
Source: [example.com/report](https://example.com/report).
[Note] See §3.2 for details <important>."""

        converter = SpeechTextConverter()
        result = converter.convert(input_text)

        # Check key conversions
        assert "twenty twenty-five" in result
        assert "forty-two percent" in result
        assert "example.com/report" in result  # Link text preserved
        assert "Note" in result
        assert "section" in result
        assert "[" not in result
        assert "]" not in result
        assert "<" not in result
        assert ">" not in result

    def test_convert_removes_all_dangerous_chars(self):
        """Ensure all dangerous characters are removed."""
        input_text = "Test {braces} and <angles> and [brackets]"
        converter = SpeechTextConverter()
        result = converter.convert(input_text)

        assert "{" not in result
        assert "}" not in result
        assert "<" not in result
        assert ">" not in result
        assert "[" not in result
        assert "]" not in result

    def test_convert_and_chunk(self):
        """Test convert_and_chunk returns proper chunks."""
        # Create long text with numbers and symbols
        input_text = "In 2025, we saw 42% growth. " * 50

        converter = SpeechTextConverter(chunk_size=500)
        chunks = converter.convert_and_chunk(input_text)

        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 500
            assert "%" not in chunk  # Should be "percent"

    def test_plain_text_output(self):
        """Ensure output is plain UTF-8 text with no markup."""
        input_text = """
# Header

This is **bold** and *italic*.

- Item 1
- Item 2

Visit [link](http://example.com).
"""
        converter = SpeechTextConverter()
        result = converter.convert(input_text)

        # No markdown remains
        assert "# " not in result  # No header markers
        assert "**" not in result  # No bold markers
        assert "](http" not in result  # No link syntax


class TestReplacementTable:
    """Test the practical replacement table from docs."""

    def test_100_to_one_hundred(self):
        """100 -> one hundred."""
        assert "one hundred" in normalize_numbers("100 items")

    def test_21st_to_twenty_first(self):
        """21st -> twenty-first."""
        assert normalize_numbers("21st") == "twenty-first"

    def test_100_dollars(self):
        """$100 -> one hundred dollars."""
        assert normalize_symbols("$100") == "one hundred dollars"

    def test_29_99_euros(self):
        """€29.99 -> twenty-nine euros and ninety-nine cents."""
        result = normalize_symbols("€29.99")
        assert "twenty-nine euros" in result
        assert "ninety-nine cents" in result

    def test_date_conversion(self):
        """10/12/2025 -> October twelve, twenty twenty-five."""
        result = normalize_dates("10/12/2025")
        assert "October" in result

    def test_time_conversion(self):
        """9:30 PM -> nine thirty p m."""
        result = normalize_symbols("9:30 PM")
        assert "nine" in result
        assert "thirty" in result

    def test_fbi_spaced(self):
        """FBI -> F B I."""
        assert normalize_acronyms("FBI") == "F B I"

    def test_percent_to_word(self):
        """% -> percent."""
        assert "percent" in normalize_symbols("50%")

    def test_ampersand_to_and(self):
        """& -> and."""
        assert normalize_symbols("&") == " and "

    def test_plus_to_word(self):
        """+ -> plus."""
        assert "plus" in normalize_symbols("1 + 1")
