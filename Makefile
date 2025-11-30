.PHONY: help init run crawl format bundle fetch test clean

help:
	@echo ""
	@echo "  init       Setup"
	@echo "  run        init + crawl + format + bundle"
	@echo "  crawl      Download new articles"
	@echo "  format     Convert to speech-friendly text"
	@echo "  bundle     Combine speech-friendly text into 6-month bundles"
	@echo "  fetch      Fetch and convert a URL (use: make fetch URL=...)"
	@echo "  test       Run tests"
	@echo "  clean      Remove cached/temp files"
	@echo ""

init:
	@echo ""
	@mkdir -p src scripts prompts data/input data/output
	@uv sync
	@echo "Project initialized successfully"
	@echo ""

run: init crawl format bundle

crawl: clean
	@echo ""
	@uv run src/crawler.py
	@echo ""

format: clean
	@echo ""
	@uv run src/transcript.py
	@echo ""

bundle: clean
	@echo ""
	@uv run src/combine_transcripts.py
	@./hook.sh
	@echo ""

fetch:
	@echo ""
ifndef URL
	@echo "Error: URL parameter required"
	@echo "Usage: make fetch URL=https://example.com/article"
	@echo ""
	@exit 1
endif
	@uv run src/fetch_article.py "$(URL)"
	@echo ""

test:
	@echo ""
	@uv sync
	@uv run python -m pytest tests/ -v
	@echo ""

clean:
	@rm -rf __pycache__ .pytest_cache .mypy_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
