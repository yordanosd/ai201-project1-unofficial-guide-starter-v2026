# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none, because the grader can't
> read it.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Week 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

## Chunking Strategy

**Chunk size:** one `##` section per chunk (212–784 characters after prefix; 353 average)
**Overlap:** 0

**Before (starter):** fixed 800-character windows with 120 overlap, `chunker.py::fallback_split`.

```text
Corpus: city_guides
  loaded   14 documents, 28,958 characters, ~2,068 characters per document
  chunked  51 chunks, 650 characters on average (shortest 24, longest 800), produced by chunker.py::fallback_split
  stored   51 chunks in 5.8s
```

The 800-char window cut straight through the labelled sections and left a
24-character tail fragment.

**After (mine):** one chunk per `##` section plus the intro paragraph, no overlap, `chunker.py::split_documents`.

```text
Corpus: city_guides
  loaded   14 documents, 28,958 characters, ~2,068 characters per document
  chunked  94 chunks, 341 characters on average (shortest 196, longest 784), produced by chunker.py::split_documents
  stored   94 chunks in 19.4s
```

Why: the 14 guides have 84 `##` sections measured at 177–712 characters, so a
section is already one complete thought and never needs splitting. The town
name appears only in the document title, so each chunk is prefixed with
`filename — title` (~40 characters) to keep its town. Overlap is 0 because
every split lands on a section boundary, not mid-sentence. Expected chunk size:
150–750 characters (criteria.md #4).

**Changed my mind partway:** the first version dropped everything above the
first `##` as "the title block" and produced 84 chunks — exactly the section
count, which looked like confirmation. Test question 1 ("How many people in
Brightwater?") then returned "not enough information" even though
`guide_brightwater.md` was retrieved: the population is in the intro paragraph
under the title, which was never indexed. The chunker now keeps that paragraph
as chunk 0 (10 of 14 files have one), giving 94 chunks.

First result against criterion 4: the longest chunk is 784, over my 750
bound. It is the longest section (712, `guide_accessibility.md` ›
Straightforward) plus the longest title (72 chars). The criterion stays as
written; this is the first thing to diagnose in Unit 2.

## Sample Chunks

Five chunks from my section-based chunker (`chunker.py::split_documents`):
one chunk per `##` section plus the intro paragraph, no overlap, each prefixed
with `filename — title` so it keeps its town. Labeled with source file and
chunk index, as printed by `python app.py chunks -n 5`.

### Chunk 1 — `guide_accessibility.md#0` — `chunker.py::split_documents`

```text
guide_accessibility.md — Getting around the region with limited mobility
An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.
```

Answers on its own: nothing — this is the intro paragraph, a preamble with no
facts. Intro chunks exist so that files whose intro *does* hold facts (e.g.
Brightwater's population) are indexed; this one is the cost of that. Worth
checking in Unit 2 whether preamble chunks ever win retrieval they shouldn't.

### Chunk 2 — `guide_corry_vale.md#5` — `chunker.py::split_documents`

```text
guide_corry_vale.md — Corry Vale
## Where to stay

Perhaps thirty beds in the entire valley, spread across two pubs and a handful of farmhouse rooms. In summer these are booked months ahead. Camping is permitted on two marked fields and nowhere else.
```

Answers on its own: "Is there accommodation in Corry Vale?"

### Chunk 3 — `guide_givens_mill.md#2` — `chunker.py::split_documents`

```text
guide_givens_mill.md — Givens Mill
## Getting around

Everything is on one street along the river. The mill is at one end and the church at the other, eight minutes apart. The riverside path continues in both directions for as far as you want to walk.
```

Answers on its own: "How far is the mill from the church in Givens Mill?"

### Chunk 4 — `guide_kestrelford.md#4` — `chunker.py::split_documents`

```text
guide_kestrelford.md — Kestrelford
## What to see

The market square on a Saturday morning is the main event and has run continuously since the 1400s. The parish church has a 13th-century tower you can climb for £2. The old trackbed walk runs six miles to the next village along an easy gradient and is the best half-day here.
```

Answers on its own: "How much does it cost to climb the church tower in Kestrelford?"

### Chunk 5 — `guide_pellew_sands.md#6` — `chunker.py::split_documents`

```text
guide_pellew_sands.md — Pellew Sands
## When to go

June and September for the beach without the crowds. July and August are busy and the town is at its most itself, for better and worse. Winter is bleak, largely closed, and has a following among people who like that sort of thing.
```

Answers on its own: "When is the best time to visit Pellew Sands?" — and it is
a criterion-5 case: a user asking about August has to be mapped to "July and
August are busy."

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**
How many people in Brightwater river town? 

**Answer:**

```
(best distance 0.259, cutoff 0.6)

Brightwater has a population of about 40,000 people, which roughly doubles during term time (guide_brightwater.md).

Sources retrieved: guide_brightwater.md, guide_regional_transport.md, guide_walking.md

1 model calls this session, 716 tokens (686 in, 30 out)
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|
|  |  |  |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.**

**2.**

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Week 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     week 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     week — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
