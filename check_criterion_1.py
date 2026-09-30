#!/usr/bin/env python3
"""
Measure criterion 1 and write the output down.

Criterion 1: for at least 4 of 5 questions, the retrieved chunks include one
that contains the answer.

    python check_criterion_1.py --run 1

Writes results/criterion_1/run1.txt and prints the same thing.

This uses the RETRIEVE path, not the ask path — `store.py::search` plus
`scorer.py::retrieval_hits` over the chunk text. The criterion is about what
retrieval pulled back, so the generated answer is not looked at and no
generation call is made. Judging retrieval by reading the answer would file a
generation failure as a retrieval failure, and week 2 is graded on naming the
stage.

Retrieval is deterministic, so the three runs produce identical output. The
judge verdicts are cached by generate.py, so re-running costs nothing after
the first pass.
"""

import argparse
import datetime as dt
import io
from pathlib import Path

import config
import questions as qs
import scorer
from store import search


def report(out: io.StringIO) -> int:
    """Write the measurement into `out`. Returns how many questions hit."""

    def say(line: str = "") -> None:
        print(line, file=out)

    items = qs.answered()
    target = 4

    say("# Criterion 1 — retrieved chunks contain the answer")
    say()
    say("- Retrieval by: `store.py::search`")
    say("- Judged by: `scorer.py::retrieval_hits` (LLM judge, over chunk text)")
    say("- Measured by: `check_criterion_1.py::report`")
    say(f"- Corpus: `{config.CORPUS}`   top-k: {config.TOP_K}")
    say(f"- Target from criteria.md section 1: at least {target} of {len(items)}")
    say(f"- When: {dt.datetime.now():%Y-%m-%d %H:%M:%S}")
    say()
    say("No generation call is made. The criterion is about what retrieval")
    say("pulled back, so the answer text is deliberately not consulted.")
    say()

    rows = []
    hits = 0
    for item in items:
        question, expects = item["question"], item.get("expects", "")
        results = search(question, top_k=config.TOP_K)
        verdict = scorer.retrieval_hits(expects, results)
        hits += verdict
        rows.append((question, expects, results, verdict))

    say("## Results")
    say()
    say("| Question | expects | Best distance | Chunks retrieved | Contains answer |")
    say("|---|---|---|---|---|")
    for question, expects, results, verdict in rows:
        best = min(r.distance for r in results)
        sources = ", ".join(sorted({r.source for r in results}))
        say(f"| {question} | `{expects}` | {best:.3f} | {sources} | "
            f"{'HIT' if verdict else 'MISS'} |")
    say()
    say(f"**{hits} of {len(items)}**")
    say()

    misses = [r for r in rows if not r[3]]
    if misses:
        say("## Misses, with every chunk retrieved")
        say()
        say("Printed in full so the verdict can be checked by hand rather than")
        say("taken on trust — the judge is a model and can be wrong.")
        say()
        for question, expects, results, _ in misses:
            say(f"### {question}")
            say()
            say(f"expects: `{expects}`")
            say()
            for r in sorted(results, key=lambda r: r.distance):
                say(f"- **{r.label}** (distance {r.distance:.3f}, "
                    f"{len(r.text)} chars)")
                say()
                say("  ```")
                for line in r.text.splitlines():
                    say(f"  {line}")
                say("  ```")
                say()

    say("## Verdict")
    say()
    if hits >= target:
        margin = hits - target
        say(f"MET — {hits} of {len(items)}, target was at least {target}.")
        if margin == 0:
            say()
            say("Exactly at target with no margin. One more miss fails it.")
    else:
        say(f"MISSED — {hits} of {len(items)}, target was at least {target}.")
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure criterion 1 and save the output.")
    parser.add_argument("--run", type=int, required=True,
                        help="which run column this is (1, 2, 3)")
    args = parser.parse_args()

    out = io.StringIO()
    report(out)
    text = out.getvalue()

    directory = config.RESULTS_DIR / "criterion_1"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"run{args.run}.txt"
    path.write_text(text, encoding="utf-8")

    print(text)
    print(f"Wrote {path.relative_to(config.ROOT)}")

    import generate
    print(generate.usage())


if __name__ == "__main__":
    main()