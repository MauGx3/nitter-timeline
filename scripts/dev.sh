#!/usr/bin/env bash
set -euo pipefail

exec uvicorn nitter_timeline.main:app --reload --port 8000
