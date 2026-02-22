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
