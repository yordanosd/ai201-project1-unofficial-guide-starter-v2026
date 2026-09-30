"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""
import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in week 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks. ⚠️ REPLACE THE BODY OF THIS IN MILESTONE 3.

    Right now it just calls the fallback. That is the plain, generic behaviour
    the brief is talking about.

    When you write your own strategy, set `produced_by` to
    "chunker.py::split_documents" so your README's Sample Chunks section names
    the right function. `app.py chunks` prints that string for you.

    Things worth thinking about before you write any code:
      - Are your documents short posts or long guides? Long guides with section header
      - Is the useful information in one sentence, or spread over a paragraph? Useful info in section header content
      - Would splitting on paragraph breaks keep more thoughts intact than
        splitting on a character count? Spliting by section headers

    Chunking Strategy:
        One chunk per `##` section, no overlap.

        city_guides is 14 markdown files, each a title line followed by short
        `##` sections (84 total, 177–712 characters). A section is already one
        complete thought, so splitting anywhere else only damages it.

        The town name lives only in the title, so every chunk is prefixed with
        "<filename> — <title>" (~40 chars) to keep its town after the split.
        Expected chunk size: 150–750 characters (criteria.md #4).
    """
    chunks = []
    for doc in documents:
        text = doc.text
        title = text.split("\n", 1)[0].lstrip("# ").strip()
        header = f"{doc.source} — {title}"
        sections = re.split(r"\n(?=## )", text)
        index = 0   # runs across the whole document, not per section: one
                    # section can now yield more than one chunk, and store.py
                    # builds Chroma ids from source+index, so a repeated index
                    # would collide and silently drop a chunk.
        for i, sec in enumerate(sections):
            body = sec.strip()
            if i == 0:
                # Intro block: drop the "# Title" line (already in the header)
                # but keep the paragraph under it — it holds facts like population.
                body = body.split("\n", 1)[1].strip() if "\n" in body else ""
                if not body:
                    continue
            for part in _fit(body, header):
                chunks.append(Chunk(
                    source=doc.source, index=index,
                    text=f"{header}\n{part}",
                    produced_by="chunker.py::split_documents",
                ))
                index += 1
    return chunks


# The bound criteria.md section 4 sets. A section is still the unit I want —
# _fit only intervenes when one is too long to fit inside it.
MAX_CHARS = 750
MIN_CHARS = 150


def _fit(body: str, header: str) -> list[str]:
    """
    Cut one section's body into pieces that fit MAX_CHARS once the header is on.

    Most sections come back unchanged — this only does work when a section is
    over the bound. In city_guides exactly one is: guide_accessibility.md's
    "Straightforward" section describes three towns in three `**Town**`
    paragraphs, which is a list rather than a single thought, so a paragraph
    break is the least damaging place to cut it.

    Splitting has a cost the size bound doesn't show: the header is re-prefixed
    onto every piece, so cutting one 784-character chunk in two adds a second
    ~72-character header. That is the price of keeping the town name on both
    halves, and it is worth paying — a chunk that has lost its town is worse
    than a chunk that is slightly short.
    """
    budget = MAX_CHARS - len(header) - 1   # -1 for the newline after the header
    if len(body) <= budget:
        return [body]

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    parts: list[str] = []
    current: list[str] = []

    for paragraph in paragraphs:
        candidate = current + [paragraph]
        if current and len("\n\n".join(candidate)) > budget:
            parts.append("\n\n".join(current))
            current = [paragraph]
        else:
            current = candidate
    if current:
        parts.append("\n\n".join(current))

    # A single paragraph longer than the budget can't be fixed by paragraph
    # breaks. Fall back to sentence ends, then to a hard cut, so the bound holds
    # whatever the corpus contains.
    fitted: list[str] = []
    for part in parts:
        fitted.extend(_split_long(part, budget) if len(part) > budget else [part])

    # Don't leave a fragment under the floor when it can ride along with its
    # neighbour instead.
    merged: list[str] = []
    for part in fitted:
        if (
            merged
            and len(part) < MIN_CHARS - len(header) - 1
            and len(merged[-1]) + len(part) + 2 <= budget
        ):
            merged[-1] = f"{merged[-1]}\n\n{part}"
        else:
            merged.append(part)
    return merged


def _split_long(text: str, budget: int) -> list[str]:
    """One over-long paragraph, cut at sentence ends where possible."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    pieces: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence
        if current and len(candidate) > budget:
            pieces.append(current)
            current = sentence
        else:
            current = candidate
        while len(current) > budget:      # a single sentence over budget
            pieces.append(current[:budget].rstrip())
            current = current[budget:].lstrip()
    if current:
        pieces.append(current)
    return pieces


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
