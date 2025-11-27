# Andrews Batch Reader

Crawls Andrew Ng's "The Batch" newsletter and generates 6-month transcript bundles optimized for text-to-speech services (such as ElevenLabs), so you can listen to them in a batch.

## Repository Structure

```
andrews-batch-reader/
├── pyproject.toml              # Project dependencies and metadata
├── Makefile                    # Build and run commands
├── CLAUDE.md                   # AI development guidelines
├── README.md                   # This file
├── hook.sh                     # Post-processing hook (customize for your needs)
├── src/
│   ├── crawler.py              # Web crawler for The Batch articles
│   ├── speech_text.py          # Text converter for speech-friendly output
│   ├── transcript.py           # Convert articles to transcripts
│   └── combine_transcripts.py  # Generate 6-month period files
├── tests/
│   └── test_speech_text.py     # Tests for text converter
└── data/
    ├── input/articles/<slug>/  # Downloaded articles
    │   ├── article.txt
    │   └── metadata.json
    └── output/
        ├── transcripts/<yyyymmdd>_<slug>.txt
        └── <year>_jan_jun.txt / <year>_jul_dec.txt  # Combined 6-month files
```

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

Initialize the project (installs dependencies):

```bash
make init
```

## Usage

### Full Pipeline

Run the complete pipeline (init, crawl, transcripts):

```bash
make run
```

### Individual Commands

```bash
make help               # Show all available commands
make crawl              # Download articles from The Batch (incremental)
make format             # Convert articles to speech-friendly text
make bundle             # Combine speech-friendly text into 6-month bundles
make test               # Run all tests
make clean              # Remove cached/temp files
```

### Crawl Articles

Download articles from The Batch newsletter:

```bash
make crawl
```

The crawler will:
- Find all articles from https://www.deeplearning.ai/the-batch/tag/letters/
- Download article text
- Skip already downloaded articles (incremental crawl)
- Save data to `data/input/articles/<article-slug>/`

### Format Articles

Convert articles to speech-friendly text:

```bash
make format
```

This converts articles by:
- Removing markdown/HTML formatting
- Spelling out numbers (42 → forty-two)
- Converting dates (10/12/2025 → October twelve, twenty twenty-five)
- Normalizing symbols ($100 → one hundred dollars, 42% → forty-two percent)
- Expanding acronyms (FBI → F B I, etc. → et cetera)
- Removing characters that harm speech quality ({}<>[])

### Bundle

Combine speech-friendly text into 6-month bundles, ordered by date (newest first):

```bash
make bundle
```

This creates separate files for each half-year period (e.g., `2024_jan_jun.txt`, `2024_jul_dec.txt`).
Each file includes intro text for articles: "The first/following article was published on [DATE]: [TITLE]"

After generating bundles, the `hook.sh` script is called automatically (see [Post-Processing Hook](#post-processing-hook)).

### Post-Processing Hook

The `hook.sh` script runs after `make bundle`. Customize it for your needs.

**Default behavior (macOS):** Copies generated files to iCloud Drive for use with ElevenReader:
```
~/Library/Mobile Documents/com~apple~CloudDocs/Elevenreader/Andrew Ng - The Batch/
```

The script creates the destination folder if it doesn't exist. On non-macOS systems, it does nothing by default. Adjust this script for your workflow.

## How It Works

1. **Crawler** (`src/crawler.py`): Uses Scrapy with Playwright to download article text from The Batch
2. **Text Converter** (`src/speech_text.py`): Transforms text to speech-friendly format
3. **Format** (`src/transcript.py`): Batch converts all articles using the text converter
4. **Bundle** (`src/combine_transcripts.py`): Combines formatted text into 6-month bundles
