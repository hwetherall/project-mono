"""
Web server entry point.
Usage: python run_web.py [--port 8000] [--host 0.0.0.0] [--reload]
"""
import os
import sys
import warnings

# Suppress requests dependency version warning (chardet 7.x / charset_normalizer 3.x
# work fine; requests only declares support for older chardet).
warnings.filterwarnings(
    "ignore",
    message=".*urllib3.*or chardet.*charset_normalizer.*doesn't match a supported version.*",
    module="requests",
)

if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Innovera Research Web UI")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for local UI development.",
    )
    args = parser.parse_args()
    uvicorn.run("api.app:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
