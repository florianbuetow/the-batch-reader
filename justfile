# justfile conventions:
# Rule 1: Use `printf` for colors, never `echo`
# Rule 2: Empty `@echo ""` lines before and after each target
# Rule 3: `help` is the default target, NOT `list`
# Rule 4: Help target groups and ordering (Setup → Pipeline → Testing)
# Rule 5: Composite targets use shebang + `set -e` for fail-fast
# Rule 6: Every target ends with a clear status message
# Rule 7: Help section groups match file ordering
# Rule 8: This rules comment block at top of file
# Rule 9: Single-line `# Description` comment above each target
# Rule 10: Python via `uv run`, never `python` or `python3`

# Default recipe: show available commands
_default:
    @just help

# Show available commands
help:
    @echo ""
    @clear
    @echo ""
    @printf "\033[0;34m=== the-batch-reader ===\033[0m\n"
    @echo ""
    @printf "\033[0;33mSetup & Lifecycle:\033[0m\n"
    @printf "  %-38s %s\n" "init" "Setup: create dirs, sync deps"
    @printf "  %-38s %s\n" "clean" "Remove cached/temp files"
    @printf "  %-38s %s\n" "help" "Show this help"
    @echo ""
    @printf "\033[0;33mRun & Pipeline:\033[0m\n"
    @printf "  %-38s %s\n" "run" "Run full pipeline: init, crawl, format, bundle"
    @echo ""
    @printf "\033[0;33mData Pipeline:\033[0m\n"
    @printf "  %-38s %s\n" "crawl" "Download new articles"
    @printf "  %-38s %s\n" "format" "Convert to speech-friendly text"
    @printf "  %-38s %s\n" "bundle" "Combine transcripts into 6-month bundles"
    @printf "  %-38s %s\n" "fetch <url> [lang]" "Fetch and convert a single URL"
    @printf "  %-38s %s\n" "convert [lang]" "Convert text to speech-friendly format"
    @echo ""
    @printf "\033[0;33mCI & Testing:\033[0m\n"
    @printf "  %-38s %s\n" "test" "Run all tests"
    @echo ""

# Setup: create dirs, sync deps
init:
    @echo ""
    @printf "\033[0;34m=== Initializing Project ===\033[0m\n"
    @mkdir -p src scripts prompts data/input data/output
    @uv sync
    @printf "\033[0;32m✓ Project initialized\033[0m\n"
    @echo ""

# Remove cached/temp files
clean:
    @echo ""
    @printf "\033[0;34m=== Cleaning ===\033[0m\n"
    @rm -rf __pycache__ .pytest_cache .mypy_cache
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @find . -type f -name "*.pyc" -delete 2>/dev/null || true
    @printf "\033[0;32m✓ Clean complete\033[0m\n"
    @echo ""

# Run full pipeline: init, crawl, format, bundle
run:
    #!/usr/bin/env bash
    set -e
    echo ""
    printf "\033[0;34m=== Running Full Pipeline ===\033[0m\n"
    echo ""
    just init
    just crawl
    just format
    just bundle
    echo ""
    printf "\033[0;32m✓ Pipeline complete\033[0m\n"
    echo ""

# Download new articles
crawl: clean
    @echo ""
    @printf "\033[0;34m=== Crawling Articles ===\033[0m\n"
    @uv run src/crawler.py
    @printf "\033[0;32m✓ Crawl complete\033[0m\n"
    @echo ""

# Convert to speech-friendly text
format: clean
    @echo ""
    @printf "\033[0;34m=== Formatting Transcripts ===\033[0m\n"
    @uv run src/transcript.py
    @printf "\033[0;32m✓ Format complete\033[0m\n"
    @echo ""

# Combine transcripts into 6-month bundles
bundle: clean
    @echo ""
    @printf "\033[0;34m=== Bundling Transcripts ===\033[0m\n"
    @uv run src/combine_transcripts.py
    @./hook.sh
    @printf "\033[0;32m✓ Bundle complete\033[0m\n"
    @echo ""

# Fetch and convert a single URL (usage: just fetch <url> [lang])
fetch url lang="":
    #!/usr/bin/env bash
    set -e
    echo ""
    printf "\033[0;34m=== Fetching Article ===\033[0m\n"
    if [ -n "{{lang}}" ]; then
        uv run src/fetch_article.py "{{url}}" --lang "{{lang}}" --skip-acronyms
    else
        uv run src/fetch_article.py "{{url}}" --skip-acronyms
    fi
    printf "\033[0;32m✓ Fetch complete\033[0m\n"
    echo ""

# Convert text to speech-friendly format (usage: just convert [lang])
convert lang="":
    #!/usr/bin/env bash
    set -e
    echo ""
    printf "\033[0;34m=== Converting Text ===\033[0m\n"
    if [ -n "{{lang}}" ]; then
        uv run src/speech_text.py --lang "{{lang}}" --skip-acronyms
    else
        uv run src/speech_text.py --skip-acronyms
    fi
    printf "\033[0;32m✓ Convert complete\033[0m\n"
    echo ""

# Run all tests
test:
    @echo ""
    @printf "\033[0;34m=== Running Tests ===\033[0m\n"
    @uv sync
    @uv run python -m pytest tests/ -v
    @printf "\033[0;32m✓ Tests passed\033[0m\n"
    @echo ""
