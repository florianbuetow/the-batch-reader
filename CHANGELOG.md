# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## 2026-04-20

### Changed

- Replaced Makefile with a justfile for colored output and simpler task running.

## 2026-02-22

### Added

- German language support with `--lang de` flag on fetch and convert commands.

### Changed

- Refactored speech text converter into a pluggable language-config architecture.

## 2025-11-30

### Added

- Added `fetch` command to download and convert a single article from any URL.

### Changed

- Removed parenthetical text from converted output to improve speech clarity.

## 2025-11-27

### Added

- Initial newsletter crawler and speech-text conversion pipeline.

### Fixed

- Fixed acronym normalization to prevent short words like "it" being spelled out.
