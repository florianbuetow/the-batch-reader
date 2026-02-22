"""Tests for German speech text conversion."""

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
