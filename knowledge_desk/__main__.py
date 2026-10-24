"""Public development probe: retrieval only, not generated answers."""
import argparse
import json

from .retrieval import search


def positive_integer(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Words or an error code to search in the fictional manuals")
    parser.add_argument("--top-k", type=positive_integer, default=3, help="Maximum results (default: 3)")
    args = parser.parse_args()
    print(json.dumps(
        {"query": args.query, "results": search(args.query, args.top_k)},
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
