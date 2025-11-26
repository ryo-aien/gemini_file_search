#!/usr/bin/env python3
"""
Export OpenAPI schema to JSON file.

Usage:
    python scripts/export_openapi.py
"""

import json
from pathlib import Path

from app.main import app


def export_openapi() -> None:
    """Export OpenAPI schema to openapi.json."""
    openapi_schema = app.openapi()

    output_path = Path(__file__).parent.parent / "openapi.json"

    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)

    print(f"OpenAPI schema exported to: {output_path}")
    print(f"Schema version: {openapi_schema.get('openapi')}")
    print(f"API title: {openapi_schema.get('info', {}).get('title')}")
    print(f"API version: {openapi_schema.get('info', {}).get('version')}")
    print(f"Endpoints: {len(openapi_schema.get('paths', {}))}")


if __name__ == "__main__":
    export_openapi()
