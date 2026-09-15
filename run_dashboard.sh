#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
if [ -f "$DIR/.venv/bin/python" ]; then
    PYTHON_EXEC="$DIR/.venv/bin/python"
elif [ -f "$DIR/venv/bin/python" ]; then
    PYTHON_EXEC="$DIR/venv/bin/python"
else
    PYTHON_EXEC="python3"
fi

echo "======================================================="
echo "Đang khởi động SEO & GEO Master Suite Dashboard..."
echo "Truy cập tại: http://localhost:8000"
echo "======================================================="

"$PYTHON_EXEC" -m uvicorn seo_geo_suite.dashboard.app:app --host 127.0.0.1 --port 8000 --reload
