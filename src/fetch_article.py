#!/usr/bin/env python3
"""Fetch and convert a single URL to speech-friendly text.

This script downloads an article from any URL and converts it to
speech-friendly format using the same converter as the main pipeline.
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from speech_text import SpeechTextConverter


def sanitize_filename(text: str) -> str:
    """Convert text to safe filename.

    Args:
        text: Text to sanitize

    Returns:
        Safe filename string
    """
    # Remove/replace unsafe characters
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    return text.lower().strip('_')


def extract_article_text(html: str, url: str) -> tuple[str, str]:
    """Extract article title and body text from HTML.

    Args:
        html: Raw HTML content
        url: Source URL (for context)

    Returns:
        Tuple of (title, body_text)
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Remove script and style elements
    for script in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        script.decompose()

    # Try to find title
    title = ''
    if soup.title:
        title = soup.title.string.strip()
    elif soup.h1:
        title = soup.h1.get_text().strip()

    # Try to find main content
    # Look for common article containers
    article_selectors = [
        'article',
        '[role="main"]',
        'main',
        '.article',
        '.post',
        '.content',
        '#content',
    ]

    content = None
    for selector in article_selectors:
        content = soup.select_one(selector)
        if content:
            break

    # Fallback to body if no article container found
    if not content:
        content = soup.body

    if not content:
        raise ValueError(f"Could not extract content from {url}")

    # Get text
    text = content.get_text(separator='\n', strip=True)

    return title, text


def fetch_and_convert(url: str, output_dir: Path) -> Path:
    """Fetch URL and convert to speech-friendly text.

    Args:
        url: URL to fetch
        output_dir: Directory to save output file

    Returns:
        Path to created output file
    """
    print(f"Fetching: {url}")

    # Fetch HTML
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; BatchReader/1.0)'
        })
        response.raise_for_status()
        html = response.text
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract content
    try:
        title, body = extract_article_text(html, url)
    except Exception as e:
        print(f"Error extracting content: {e}", file=sys.stderr)
        sys.exit(1)

    if not body.strip():
        print("Error: No content extracted from URL", file=sys.stderr)
        sys.exit(1)

    print(f"Extracted: {title if title else 'Untitled'}")
    print(f"Content length: {len(body)} characters")

    # Combine title and body
    full_text = f"{title}\n\n{body}" if title else body

    # Convert to speech-friendly format
    print("Converting to speech-friendly format...")
    converter = SpeechTextConverter()
    speech_text = converter.convert(full_text)

    # Generate output filename
    date_str = datetime.now().strftime('%Y%m%d')
    if title:
        filename = f"{date_str}_{sanitize_filename(title)[:50]}.txt"
    else:
        # Use domain from URL
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace('.', '_')
        filename = f"{date_str}_{domain}.txt"

    # Save to output directory
    output_path = output_dir / filename
    output_path.write_text(speech_text, encoding='utf-8')

    print(f"Saved to: {output_path}")
    print(f"Output length: {len(speech_text)} characters")

    return output_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Fetch and convert a URL to speech-friendly text'
    )
    parser.add_argument(
        'url',
        help='URL to fetch and convert'
    )
    parser.add_argument(
        '-o', '--output-dir',
        default='data/output/misc',
        help='Output directory (default: data/output/misc)'
    )

    args = parser.parse_args()

    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Fetch and convert
    output_path = fetch_and_convert(args.url, output_dir)

    print("\nDone!")


if __name__ == '__main__':
    main()
