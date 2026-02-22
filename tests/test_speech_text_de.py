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
