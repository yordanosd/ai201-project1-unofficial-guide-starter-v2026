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

I selected the city_guides corpus: 14 travel guides to towns in a fictional
region. You can ask about a specific town or any travel question, from when
to go to accessibility. If the guides cover the topic you get a short answer
that cites the guide it came from. If they don't, it says so.

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

**Question:** Is Brightwater busy in October?

**Answer:**

```text
  (best distance 0.314, cutoff 0.6)

Yes, Brightwater is at its busiest from late September through November as term starts.

This information comes from `guide_brightwater.md` and `guide_seasons.md`.

Sources retrieved: guide_brightwater.md, guide_regional_transport.md, guide_seasons.md
```

The user asked by month; the document says "Late September through November
the town is at its busiest." The answer maps one to the other and names both
files it drew on — criterion 5's range case and criterion 2, on the first run.

**My relevance cutoff:** 0.6 (the starter default, kept on purpose)

I ran my five test questions and the five `OUT_OF_SCOPE` questions through
`python app.py retrieve` and recorded the best distance for each. In-scope
questions ranged from 0.259 to 0.374; out-of-scope from 0.798 to 1.002. Two
clear groups with no overlap. 0.6 isn't too low: the highest in-scope
distance is 0.374, so no answerable question is refused. It isn't too high:
the lowest out-of-scope distance is 0.798, so nothing gets made up. It sits
closer to the out-of-scope group than the in-scope one, which leaves room for
harder in-scope questions to still pass, at the cost that an out-of-scope
question close to the topic (a real town the corpus doesn't cover, say) could
slip through. I would need more data points to make a better determination,
but with a gap this wide I think 0.6 is a fair result. If I moved it, I'd go
lower (about 0.55) to guard against that near-topic case. Worth testing in
the future. 

| Question | In corpus? | Best distance |
|---|---|---|
| How many people in Brightwater river town? | yes | 0.259 |
| Can I visit the mill in Givens Mill in December? | yes | 0.306 |
| Is Brightwater busy in October? | yes | 0.314 |
| How much does the city museum in Marchwood for entry? | yes | 0.349 |
| Does Elder Ness have public transport? | yes | 0.374 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.798 |
| What is the capital of Mongolia? | no | 0.819 |
| How do I write a for loop in Rust? | no | 0.850 |
| How do I change the oil in a diesel engine? | no | 0.937 |
| Who won the 1994 World Cup? | no | 1.002 |

Before the chunker fix, "How many people in Brightwater" had a best distance
of 0.452 with the wrong file (`guide_regional_transport.md`) at rank 1 and the
answer "not enough information" — because the population sentence was never
indexed. After keeping the intro paragraph as a chunk: 0.259, right file,
right answer. See Chunking Strategy.

**Retrieval finding:** on "Does Elder Ness have public transport?" the chunk
that holds the answer (`guide_elder_ness.md` › Getting there: "No public
transport of any kind") is not in the top 5. That section leads with tide
flooding, so its embedding is mostly about tides, and "Getting around" (on
foot, car park) outranks it. The model still answered correctly from "on
foot" and cited the file, but not from the sentence I filed as `expects`.
I tested k=10 and the chunk came back with the right answer; then k=6, and
it came back at rank 6. Kept k=5 for submission so the Unit 2 before/after
is measurable. Hypothesis for Unit 2: raise k to 6.

## How I Used AI

**1.** I gave Claude my chunking design (split at `##` headers, prefix each
chunk with filename and title, no overlap) and asked for the function. It
came back dropping everything above the first `##` as "the title block,"
which also dropped the intro paragraph where facts like Brightwater's
population live. I only caught it because test question 1 returned "not
enough information." I had it keep the intro paragraph as chunk 0.

**2.** I wrote my five test questions and two criteria and asked Claude to
rate them and say how a grader would test each from the sentence alone. My
first questions ("where to go in winter," "best for accessibility") scored
low because they were recommendations with no right answer; I rewrote them
backwards from specific sentences in the docs. For criterion 4 it measured
the 84 sections (177–712 chars) so my size bound came from the corpus
instead of a guess. I wrote every criterion and reason myself.

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

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
