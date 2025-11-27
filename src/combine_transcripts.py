"""Combine all transcripts into 6-month period files, ordered by date."""

import json
from datetime import datetime
from pathlib import Path
from speech_text import SpeechTextConverter


DATA_DIR = Path(__file__).parent.parent / "data"
INPUT_DIR = DATA_DIR / "input" / "articles"
TRANSCRIPTS_DIR = DATA_DIR / "output" / "transcripts"
OUTPUT_DIR = DATA_DIR / "output"


def get_article_metadata(slug: str) -> dict | None:
    """Load metadata for an article by slug."""
    metadata_file = INPUT_DIR / slug / "metadata.json"
    if metadata_file.exists():
        return json.loads(metadata_file.read_text(encoding='utf-8'))
    return None


def parse_date(date_str: str) -> datetime:
    """Parse ISO date string to datetime."""
    # Handle format like "2022-01-12T11:58:40.000-08:00"
    # Remove milliseconds and timezone for simpler parsing
    date_str = date_str.split('.')[0]
    return datetime.fromisoformat(date_str)


def format_date_for_speech(dt: datetime) -> str:
    """Format datetime for spoken text."""
    # Format: "January 12th, 2022"
    day = dt.day
    if 11 <= day <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    return f"{dt.strftime('%B')} {day}{suffix}, {dt.year}"


def get_period_key(dt: datetime) -> str:
    """Get the 6-month period key for a date (e.g., '2024_H1' or '2024_H2')."""
    half = "H1" if dt.month <= 6 else "H2"
    return f"{dt.year}_{half}"


def get_period_filename(period_key: str) -> str:
    """Convert period key to filename (e.g., '2024_H1' -> '2024_jan_jun.txt')."""
    year, half = period_key.split("_")
    if half == "H1":
        return f"{year}_jan_jun.txt"
    return f"{year}_jul_dec.txt"


def combine_transcripts() -> list[Path]:
    """Combine transcripts into 6-month period files, ordered by date (newest first).

    Returns list of generated file paths.
    """
    print("Combining transcripts into 6-month period files...")

    transcripts = list(TRANSCRIPTS_DIR.glob("*.txt"))

    if not transcripts:
        print("No transcripts found in data/output/transcripts/")
        return []

    converter = SpeechTextConverter()

    # Collect transcript data with metadata
    articles = []
    for transcript_file in transcripts:
        filename = transcript_file.stem
        # Handle both old format (slug.txt) and new format (yyyymmdd_slug.txt)
        if '_' in filename and filename[:8].isdigit():
            slug = filename[9:]  # Remove yyyymmdd_ prefix
        else:
            slug = filename
        metadata = get_article_metadata(slug)

        if not metadata:
            print(f"Warning: No metadata for {slug}, skipping")
            continue

        content = transcript_file.read_text(encoding='utf-8')
        date = parse_date(metadata['published_at'])
        title = metadata['title']

        articles.append({
            'slug': slug,
            'title': title,
            'date': date,
            'content': content,
            'period': get_period_key(date),
        })

    # Group articles by 6-month period
    periods: dict[str, list[dict]] = {}
    for article in articles:
        period = article['period']
        if period not in periods:
            periods[period] = []
        periods[period].append(article)

    # Sort articles within each period by date (newest first)
    for period_articles in periods.values():
        period_articles.sort(key=lambda x: x['date'], reverse=True)

    # Generate one file per period
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated_files = []

    for period_key in sorted(periods.keys(), reverse=True):
        period_articles = periods[period_key]
        combined_parts = []

        for i, article in enumerate(period_articles):
            date_str = format_date_for_speech(article['date'])
            # Process title through speech text converter
            title_processed = converter.convert(article['title'])

            if i == 0:
                intro = f"The first article was published on {date_str}:\n\n{title_processed}"
            else:
                intro = f"The following article was published on {date_str}:\n\n{title_processed}"

            combined_parts.append(intro)
            combined_parts.append("")  # Blank line
            combined_parts.append(article['content'])
            combined_parts.append("")  # Blank line between articles
            combined_parts.append("")

        # Write period file
        output_file = OUTPUT_DIR / get_period_filename(period_key)
        combined_text = '\n'.join(combined_parts).strip()
        output_file.write_text(combined_text, encoding='utf-8')
        generated_files.append(output_file)

        print(f"Generated {output_file.name}: {len(period_articles)} articles, {len(combined_text):,} characters")

    print()  # Empty line before summary
    print(f"Total: {len(generated_files)} period files, {len(articles)} articles")
    return generated_files


if __name__ == "__main__":
    combine_transcripts()
