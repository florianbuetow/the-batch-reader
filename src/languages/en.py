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
