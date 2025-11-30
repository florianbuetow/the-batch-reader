# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Crawls Andrew Ng's "The Batch" newsletter and generates 6-month transcript bundles optimized for text to speech playback.

## Commands

```bash
make help               # Show all targets
make init               # Setup: create dirs, sync deps
make run                # Run full pipeline: init, crawl, format
make crawl              # Download new articles
make format             # Convert to speech-friendly text
make bundle             # Combine speech-friendly text into 6-month bundles
make fetch URL=<url>    # Fetch and convert a one-off URL
make test               # Run all tests
make clean              # Remove cached/temp files
```

## Python Execution

**Always use the Makefile** - never run `uv`, `python`, `python3`, or `pip` directly.

```bash
make help    # Show all available commands
make init    # Setup project and install dependencies
make test    # Run tests
```

## Architecture

### Crawler (`src/crawler.py`)

Uses Scrapy to crawl articles:

1. **Listing pages**: Parses `__NEXT_DATA__` JSON from deeplearning.ai/the-batch/tag/letters/ to get article slugs
2. **Article pages**: Extracts text from `__NEXT_DATA__` JSON (more reliable than DOM parsing)
3. **Incremental crawl**: Skips articles where `data/input/articles/<slug>/article.txt` exists

### Text Converter (`src/speech_text.py`)

Converts text to speech-friendly format with one function per rule:

- `strip_markdown()` / `strip_html()` - Remove markup
- `normalize_whitespace()` - Fix line endings and spacing
- `remove_dangerous_punctuation()` - Remove `{}<>[]` (causes low quality speech)
- `strip_control_characters()` / `remove_emojis()` / `replace_special_unicode()` - Clean weird chars
- `normalize_numbers()` - `42` → `forty-two`, `2025` → `twenty twenty-five`
- `normalize_dates()` - `10/12/2025` → `October twelve, twenty twenty-five`
- `normalize_symbols()` - `$100` → `one hundred dollars`, `42%` → `forty-two percent`
- `normalize_acronyms()` - `FBI` → `F B I`, `etc.` → `et cetera`
- `flatten_lists()` - Bullet points → prose with "Firstly, Secondly..."
- `chunk_text()` - Split into <900 char chunks at sentence boundaries

### Format (`src/transcript.py`)

Converts articles to speech-friendly text using `SpeechTextConverter`.

### Bundle (`src/combine_transcripts.py`)

Combines speech-friendly text into 6-month bundles (e.g., `2024_jan_jun.txt`, `2024_jul_dec.txt`).
Articles within each file are ordered by date (newest first), with intro text:
"The first/following article was published on [DATE]: [TITLE]"

### Fetch (`src/fetch_article.py`)

Fetches and converts a single article from any URL. Uses `requests` and `BeautifulSoup` to download and extract content, then applies `SpeechTextConverter` transformations. Output saved to `data/output/misc/` with auto-generated filename based on date and title.

### Post-Processing Hook (`hook.sh`)

Called by `make bundle` after generating files. Default behavior on macOS:
copies output files to iCloud Drive (`~/Library/Mobile Documents/com~apple~CloudDocs/Elevenreader/Andrew Ng - The Batch/`).

## Data Organization

```
data/input/articles/<slug>/
├── article.txt      # Plain text content
└── metadata.json    # Title, URL, dates

data/output/
├── transcripts/<yyyymmdd>_<slug>.txt  # Individual speech-friendly transcripts
├── misc/<yyyymmdd>_<title>.txt         # Fetched articles
└── <year>_jan_jun.txt / <year>_jul_dec.txt  # 6-month bundles
```

## Testing Guidelines

- **ALWAYS write unit tests** for bug fixes and new features
- Add tests to `tests/test_speech_text.py`
- Run `make test` to verify all tests pass
- Never skip test creation - if you fixed a bug, write a test that would have caught it

## Git Commit Guidelines

- Never include AI attribution ("Generated with Claude Code", "Co-Authored-By: Claude")
- Never use `git add -A` or `git add .` - stage files explicitly

## Key Constraints

- All source code in `src/`, never in project root
- Extract data from `__NEXT_DATA__` JSON when available
- Crawler continues on individual article failures
- Rate limit: 2 second delay between requests
