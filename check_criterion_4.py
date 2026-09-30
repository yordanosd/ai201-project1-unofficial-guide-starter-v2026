#!/usr/bin/env python3
"""
Measure criterion 4 and write the output down.

Criterion 4 has two halves, and this checks them separately:

  (a) every chunk's text begins with its own source filename
  (b) every chunk is between 150 and 750 characters, header included

    python check_criterion_4.py --run 1

Writes results/criterion_4/run1.txt and prints the same thing. Run it three
times to fill the three run columns.

Chunking is deterministic — `chunker.py::split_documents` produces the same
chunks from the same corpus every time — so the three files will be identical.
That is the point: three identical passes are what shows the measurement is
deterministic, the same argument run_eval.py makes for the relevance gate.

Costs no model calls. Chunking runs entirely on your machine.
"""

import argparse
import datetime as dt
import io
from pathlib import Path

import chunker
import config
import ingest

# The bound from criteria.md section 4. Not read from config.py on purpose:
# CHUNK_SIZE is an instruction to the chunker, this is the standard the
# criterion set, and conflating them would let a chunker change silently
# rewrite the target.
MIN_CHARS = 150
MAX_CHARS = 750


def report(out: io.StringIO) -> bool:
    """Write the measurement into `out`. Returns True if criterion 4 holds."""
    documents = ingest.load_documents(config.CORPUS)
    chunks = chunker.split_documents(documents)

    def say(line: str = "") -> None:
        print(line, file=out)

    say(f"# Criterion 4 — chunks carry their document header")
    say()
    say(f"- Produced by: `chunker.py::split_documents`")
    say(f"- Measured by: `check_criterion_4.py::report`")
    say(f"- Summary line from: `chunker.py::describe`")
    say(f"- Corpus: `{config.CORPUS}` ({len(documents)} documents)")
    say(f"- Bound from criteria.md section 4: {MIN_CHARS}-{MAX_CHARS} characters")
    say(f"- When: {dt.datetime.now():%Y-%m-%d %H:%M:%S}")
    say()
    say("Costs no model calls — chunking runs locally.")
    say()
    say(chunker.describe(chunks))
    say()

    bad_header = [c for c in chunks if not c.text.lstrip().startswith(c.source)]
    bad_length = [c for c in chunks if not (MIN_CHARS <= len(c.text) <= MAX_CHARS)]

    total = len(chunks)
    say("## The two checks")
    say()
    say(f"| Check | Result |")
    say(f"|---|---|")
    say(f"| (a) text begins with its source filename | {total - len(bad_header)}/{total} |")
    say(f"| (b) {MIN_CHARS} <= length <= {MAX_CHARS} | {total - len(bad_length)}/{total} |")
    say()

    sizes = sorted(len(c.text) for c in chunks)
    say(f"Size distribution: shortest {sizes[0]}, median {sizes[len(sizes) // 2]}, "
        f"longest {sizes[-1]}.")
    say(f"Five largest: {sizes[-5:]}")
    say()

    if bad_header:
        say("## Chunks missing their header")
        say()
        for c in bad_header:
            say(f"- `{c.source}#{c.index}` begins {c.text.lstrip()[:60]!r}")
        say()

    if bad_length:
        say("## Chunks outside the bound")
        say()
        for c in bad_length:
            over = len(c.text) - MAX_CHARS
            under = MIN_CHARS - len(c.text)
            how = f"{over} over the ceiling" if over > 0 else f"{under} under the floor"
            say(f"- `{c.source}#{c.index}` — {len(c.text)} characters, {how}")
        say()
        say("Full text of the first one:")
        say()
        say("```")
        say(bad_length[0].text)
        say("```")
        say()

    passed = not bad_header and not bad_length
    say("## Verdict")
    say()
    if passed:
        say(f"MET — all {total} chunks carry a header and sit inside "
            f"{MIN_CHARS}-{MAX_CHARS} characters.")
    else:
        say(f"MISSED — {len(bad_header)} chunk(s) without a header, "
            f"{len(bad_length)} outside {MIN_CHARS}-{MAX_CHARS}. "
            f"Target was every chunk, so any failure is a miss.")
    return passed


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure criterion 4 and save the output.")
    parser.add_argument("--run", type=int, required=True,
                        help="which run column this is (1, 2, 3)")
    parser.add_argument("--label", default="",
                        help="name this measurement, e.g. before/after. Writes "
                             "run1_after.txt instead of run1.txt, so an earlier "
                             "measurement is never overwritten.")
    args = parser.parse_args()

    out = io.StringIO()
    report(out)
    text = out.getvalue()

    directory = config.RESULTS_DIR / "criterion_4"
    directory.mkdir(parents=True, exist_ok=True)
    suffix = f"_{args.label}" if args.label else ""
    path = directory / f"run{args.run}{suffix}.txt"
    if path.exists() and not args.label:
        raise SystemExit(
            f"{path.relative_to(config.ROOT)} already exists.\n"
            f"Pass --label to write alongside it instead of over it — an "
            f"earlier measurement is evidence and does not get overwritten.\n"
            f"  python check_criterion_4.py --run {args.run} --label after"
        )
    path.write_text(text, encoding="utf-8")

    print(text)
    print(f"Wrote {path.relative_to(config.ROOT)}")
    print("Commit it — it's the evidence the measurement happened.")


if __name__ == "__main__":
    main()
