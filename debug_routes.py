#!/usr/bin/env python3
"""
Debug script to show all registered routes in the FastAPI application.
"""

from app.main import app


def main() -> None:
    """Display all registered routes."""
    print("=" * 80)
    print("Registered Routes in FastAPI Application")
    print("=" * 80)
    print()

    routes_by_tag: dict[str, list[tuple[str, str, str]]] = {}

    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            methods = ", ".join(route.methods - {"HEAD", "OPTIONS"})
            path = route.path
            name = route.name if hasattr(route, "name") else "unknown"
            tags = getattr(route, "tags", ["untagged"])
            tag = tags[0] if tags else "untagged"

            if tag not in routes_by_tag:
                routes_by_tag[tag] = []
            routes_by_tag[tag].append((methods, path, name))

    for tag in sorted(routes_by_tag.keys()):
        print(f"\n[{tag.upper()}]")
        print("-" * 80)
        for methods, path, name in sorted(routes_by_tag[tag], key=lambda x: x[1]):
            print(f"  {methods:8s} {path:50s} ({name})")

    print()
    print("=" * 80)
    print(f"Total routes: {len(app.routes)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
