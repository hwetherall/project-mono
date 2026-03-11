"""
Web server entry point.
Usage: python run_web.py [--port 8000] [--host 0.0.0.0]
"""
import os
import sys

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
    args = parser.parse_args()
    uvicorn.run("api.app:app", host=args.host, port=args.port, reload=True)


if __name__ == "__main__":
    main()
