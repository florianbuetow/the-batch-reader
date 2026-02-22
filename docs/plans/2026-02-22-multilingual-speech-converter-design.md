# Multilingual Speech Text Converter

## Goal

Add German language support to `SpeechTextConverter` via an explicit `lang` flag, so one-off German text files can be cleaned for TTS. English remains the default. The Batch crawler pipeline is unaffected.

## Approach: Language config dicts

Each language provides a data dict consumed by the language-sensitive converter functions. Language-neutral functions (markdown/HTML stripping, whitespace, dangerous punctuation, control characters, emojis, chunking) stay unchanged.

## Language data structure

Each language module exports a dict with:

| Key | Type | Purpose |
|-----|------|---------|
| `ones` | list[str] | Numbers 0-19 as words |
| `tens` | list[str] | Multiples of 10 (20-90) |
| `scales` | list[str] | thousand, million, billion, trillion |
| `hundred` | str | Word for "hundred" |
| `ordinals` | dict[str, str] | "1st" -> "first" / "1." -> "erste" |
| `months` | dict[str, str] | "01" -> month name |
| `list_ordinals` | list[str] | "Firstly" / "Erstens" for flatten_lists |
| `currency_names` | dict[str, str] | "$" -> "dollars" / "Dollar" |
| `currency_subunit` | dict[str, str] | "$" -> "cents" / "Cent" |
| `symbol_words` | dict[str, str] | "percent" -> "Prozent", etc. |
| `acronyms_letter` | set[str] | Acronyms to spell letter-by-letter |
| `acronyms_expanded` | dict[str, str] | Abbreviation expansions |
| `templates` | dict[str, str] | Table intro, code block placeholder |
| `number_to_words` | Callable | Language-specific number-to-words function |

German needs a dedicated `number_to_words` function because German builds compound numbers differently (ones before tens: 21 = "einundzwanzig").

## File layout

### New files

- `src/languages/__init__.py` - exports `LANGUAGES` dict and `get_language(code)` helper
- `src/languages/en.py` - English data extracted from current `speech_text.py` constants
- `src/languages/de.py` - German data and `number_to_words_de()` function
- `tests/test_speech_text_de.py` - German-specific tests

### Changed files

- `src/speech_text.py` - `SpeechTextConverter(lang="en")` gains lang param; language-sensitive functions receive lang config
- `src/fetch_article.py` - gains `--lang` CLI flag
- `Makefile` - `make fetch` gains optional `LANG=de`
- `tests/test_speech_text.py` - unchanged (tests English default)

### Unchanged files

- `src/transcript.py` - always English for The Batch
- `src/crawler.py` - unaffected
- `src/combine_transcripts.py` - unaffected

## Function changes

Language-sensitive (receive lang config):
- `normalize_numbers()`, `normalize_dates()`, `normalize_symbols()`
- `normalize_acronyms()`, `flatten_lists()`, `flatten_tables()`
- `remove_code_blocks()`

Language-neutral (no changes):
- `strip_markdown()`, `strip_html()`, `remove_parenthetical()`
- `normalize_whitespace()`, `remove_dangerous_punctuation()`
- `strip_control_characters()`, `remove_emojis()`, `replace_special_unicode()`
- `chunk_text()`

## CLI usage

```bash
# English (default, unchanged)
make fetch URL=https://example.com

# German
make fetch URL=https://example.com LANG=de

# stdin
echo "text" | python src/speech_text.py --lang de
```

## Testing

- Existing English tests pass unchanged (default lang="en")
- New German tests cover: numbers ("zweiundvierzig"), dates (German months), symbols ("Prozent", "Dollar"), lists ("Erstens, Zweitens"), acronyms (German expansions like "bzw" -> "beziehungsweise")
