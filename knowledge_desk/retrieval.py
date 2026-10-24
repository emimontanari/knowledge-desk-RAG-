"""Lexical retrieval over heading-delimited Markdown sections."""
import re
import unicodedata
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[1] / "corpus"


def tokens(text: str) -> set[str]:
    """Normalize accents and case; keep error codes such as AUTH_042 intact."""
    normalized = unicodedata.normalize("NFKD", text.casefold())
    plain = "".join(char for char in normalized if not unicodedata.combining(char))
    return set(re.findall(r"\w+", plain))


def sections():
    """Each Markdown heading starts a chunk with a traceable source."""
    for path in sorted(CORPUS.glob("*.md")):
        heading, lines = "", []
        for line in [*path.read_text(encoding="utf-8").splitlines(), "# END"]:
            if line.startswith("#"):
                text = "\n".join(lines).strip()
                if text:
                    yield {"source": f"corpus/{path.name}", "heading": heading, "text": text}
                heading, lines = line.lstrip("#").strip(), []
            else:
                lines.append(line)


def search(query: str, top_k: int = 3) -> list[dict]:
    """Score = distinct query tokens also present in heading or section text."""
    query_tokens = tokens(query)
    results = []
    for section in sections():
        score = len(query_tokens & tokens(section["heading"] + " " + section["text"]))
        if score:
            results.append({**section, "score": score})
    return sorted(
        results, key=lambda item: (-item["score"], item["source"], item["heading"])
    )[:top_k]
