# KnowledgeDesk

A retrieval-first learning project toward a no-code platform for document-backed
assistants. This first increment retrieves evidence only: it does not generate
answers, use embeddings, call a provider, or expose a dashboard.

## Run the first increment

Requires Python 3.12 or later, with no external dependencies. From this folder:

```bash
python3 -m knowledge_desk "AUTH_042" --top-k 1
python3 -m knowledge_desk "recuperar acceso cuenta"
python3 -m knowledge_desk "Olvidé mi clave"
python3 -m unittest discover -s tests -v
```

The first query returns the account recovery section and its source. The third
returns no results, although a person might connect it to account recovery:
there are no matching tokens. This is a lexical baseline, not semantic search.
An empty result means no lexical evidence was retrieved, not that the knowledge
base definitively contains no answer.

## How it works

```text
Fictional Markdown manuals → heading-delimited chunks
Question → normalized word tokens → overlap ranking → evidence with sources
```

1. Each heading starts a section. Preserve its relative source path and heading.
2. Normalize case and accents, keeping underscore codes such as `AUTH_042` intact.
3. Score each chunk by distinct query tokens present in its heading or text.
4. Sort descending by score, then source and heading for deterministic ties.
5. Return at most `--top-k` results. Reject non-positive limits; no matches gives
   an empty list. Scores are token counts, **not confidence estimates**.

## Source map

| Path | Responsibility |
|---|---|
| `knowledge_desk/retrieval.py` | Tokenization, section loading, lexical ranking |
| `knowledge_desk/__main__.py` | CLI arguments and JSON output |
| `corpus/*.md` | Synthetic DeskFlow software manuals; Spanish body text is test data |
| `tests/test_cli.py` | Public CLI tests for retrieval, attribution, ranking, and invalid limits |
| `pyproject.toml` | Python requirement and project metadata; no dependencies |

## Limits and next learning step

There is no stopword removal, synonym handling, stemming, semantic understanding,
or relevance threshold beyond one matching token. Common words can cause irrelevant
results. Heading-based chunks have no token budget and lose higher-level context.
No uploads, persistence, assistant isolation, identity, or production controls exist.

Next: discuss a paraphrase the baseline misses, define expected evidence for a
small question set, then compare retrieval approaches before adding generation.
The CLI is a development probe; it is not the final user-facing product.
