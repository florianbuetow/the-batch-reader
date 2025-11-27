"""Convert article.txt files to speech-friendly transcripts."""

import json
from datetime import datetime
from pathlib import Path
from speech_text import SpeechTextConverter


DATA_DIR = Path(__file__).parent.parent / "data"
INPUT_DIR = DATA_DIR / "input" / "articles"
OUTPUT_DIR = DATA_DIR / "output" / "transcripts"


def extract_content(text: str) -> str:
    """Extract content after the header section."""
    lines = text.split('\n')
    content_start = 0
    for i, line in enumerate(lines):
        if line.strip() == '---':
            content_start = i + 1
            break
    return '\n'.join(lines[content_start:])


def get_publication_date(slug: str) -> str | None:
    """Get publication date from metadata as yyyymmdd string."""
    metadata_file = INPUT_DIR / slug / "metadata.json"
    if metadata_file.exists():
        metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
        date_str = metadata.get('published_at', '')
        if date_str:
            # Parse ISO date like "2022-01-12T11:58:40.000-08:00"
            dt = datetime.fromisoformat(date_str.split('.')[0])
            return dt.strftime('%Y%m%d')
    return None


def convert_articles():
    """Convert all article.txt files to speech-friendly transcripts."""
    print("Converting articles to speech-friendly transcripts...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    articles = list(INPUT_DIR.glob("*/article.txt"))

    if not articles:
        print("No articles found in data/input/articles/")
        return

    converter = SpeechTextConverter()
    converted = 0
    skipped = 0

    for article_file in articles:
        slug = article_file.parent.name
        date_prefix = get_publication_date(slug)

        if date_prefix:
            output_file = OUTPUT_DIR / f"{date_prefix}_{slug}.txt"
        else:
            output_file = OUTPUT_DIR / f"{slug}.txt"

        # Skip if already converted
        if output_file.exists():
            skipped += 1
            continue

        # Read article, extract content after header, convert to speech-friendly format
        text = article_file.read_text(encoding='utf-8')
        content = extract_content(text)
        clean = converter.convert(content)

        # Write the transcript
        output_file.write_text(clean, encoding='utf-8')
        print(f"Converted: {output_file.name}")
        converted += 1

    print()  # Empty line before summary
    print(f"Done. Converted: {converted}, Skipped: {skipped}")


if __name__ == "__main__":
    convert_articles()
