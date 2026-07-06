# Central Configurations

This directory contains system logging and monitoring configurations:

## Directory Index
- `logging.conf`: Unified Python logging layout configurations.
- `prometheus.yml`: Scraper configs for GKE metrics.

## Core Guidelines
- Format logs in JSON to ensure compatibility with Cloud Logging.
- Audit all administrative command overrides (e.g., signage overrides, emergency alerts).
