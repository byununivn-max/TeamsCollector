#!/bin/bash
# 현재 디렉토리의 Python 가상 환경을 사용하거나, 시스템 Python을 사용하여 진행 상황 확인 스크립트를 실행합니다.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

if [ -f "venv/bin/python" ]; then
    venv/bin/python check_progress.py "$@"
else
    python3 check_progress.py "$@"
fi
