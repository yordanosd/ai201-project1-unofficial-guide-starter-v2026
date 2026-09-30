# The Unofficial Guide

Yordanos Dirar — corpus: city_guides

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


Source run: `results/run_2026-09-28_1503_before.md` — `python run_eval.py --label before`,
corpus `city_guides`, top-k 5, relevance cutoff 0.6, caching off.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunks contain the answer | 4 of 5 | 4/5 | 4/5 | 4/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. The relevance gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks carry their document header | 94 of 94 | 93/94 | 93/94 | 93/94 | MISSED |
| 5. A user's time reference maps to the document's season or date range | 2 of 2 | 2/2 | 2/2 | 2/2 | MET |

Criteria 1, 3 and 4 come out identical in all three columns because each is
measured on a deterministic stage — `store.py::search` returns the same chunks
for the same question, the gate is a comparison against a fixed number, and
`chunker.py::split_documents` produces the same 94 chunks every time. Criteria
2 and 5 depend on generated text and could have moved between runs. They
didn't: all three answers to each question named a source and gave a time
period.

### Real output

**Criterion 1 — retrieved chunks contain the answer.** Judged over chunk text
by `scorer.py::retrieval_hits`, on chunks from `store.py::search`. 4 of 5 hit;
the miss was "Does Elder Ness have public transport?" (`expects: "no public
transport"`). All five retrieved chunks came from the right document, and the
closest one is this — the corpus never states the fact, it only implies it:

```
guide_elder_ness.md — Elder Ness ## Getting around
On foot. The village is one street. The lighthouse is a 25-minute walk along
the shingle, which is harder going than the distance suggests. There is one
car park at the village and parking anywhere else on the headland is
discouraged.
```

**Criterion 2 — every answer names a source.** Produced by
`generate.py::answer_from_chunks`, run 1:

```
Brightwater has a population of about 40,000 people, which roughly doubles
during term time (from guide_brightwater.md).
```

**Criterion 3 — the gate stops out-of-corpus questions.** Produced by
`run_eval.py::check_out_of_scope`, cutoff 0.6, refused 5 of 5. No model call
was made for any of these — a refused question never reaches the model:

```
| Out-of-scope question                                       | Best distance | Gate    |
| What is the capital of Mongolia?                            | 0.819         | refused |
| How do I change the oil in a diesel engine?                 | 0.937         | refused |
| Who won the 1994 World Cup?                                 | 1.002         | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.798         | refused |
| How do I write a for loop in Rust?                          | 0.850         | refused |
```

**Criterion 4 — chunks carry their document header.** Two halves, measured
separately. The size half comes from `chunker.py::describe`:

```
$ python chunker.py
94 chunks, 341 characters on average (shortest 196, longest 784), produced by chunker.py::split_documents
```

`longest 784` against a 750-character ceiling is the miss — one chunk, 34
characters over. Second-largest is 680, so it's a single outlier rather than a
general drift. The header half checks that each chunk's text begins with its
own source filename:

```
$ python -c "import chunker, ingest, config; \
  cs = chunker.split_documents(ingest.load_documents(config.CORPUS)); \
  print(sum(c.text.lstrip().startswith(c.source) for c in cs), '/', len(cs))"
94 / 94
```

The offending chunk, from `python app.py chunks --from-doc guide_accessibility`:

```
======================================================================
Chunk 2  |  source: guide_accessibility.md#1  |  produced by: chunker.py::split_documents
======================================================================
guide_accessibility.md — Getting around the region with limited mobility
## Straightforward

**Thornby Wells** is the easiest town in the region. It is flat, compact, and
everything is within three minutes of everything else. Parking is free for two
hours anywhere in town and the station is central. The pump room and gardens
are level throughout.

**Marchwood** has a modern tram network with level boarding on all four lines,
running every 8 minutes on weekdays. The city museum and covered market are both
step-free. The distances between districts are the main consideration.

**Brightwater** is level along the river and through the centre. The mill museum
is step-free. The station is a 15-minute walk from campus on flat ground, or the
[...]
```

The header is present, so this chunk passes (a) and fails (b) only.

**Criterion 5 — a time reference maps to the document's season or date range.**
Produced by `generate.py::answer_from_chunks`. Both questions, run 1:

```
No, you cannot visit the mill in December because it is closed entirely in
winter and only runs from March to November (`guide_givens_mill.md`).
```

```
Yes, Brightwater is at its busiest from late September through November.
Source: `guide_brightwater.md` and `guide_seasons.md`
```

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     week — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunks contain the answer | MET | 4 of 5, judged by `scorer.py::retrieval_hits` against the chunk text `store.py::search` returned — deliberately not against the generated answer, so a generation failure can't be filed as a retrieval one. This is **exactly** the target with no margin: one more miss and it fails.<br><br>The miss was "Does Elder Ness have public transport?" and I don't think the judge got it right. All five chunks came from the right document, and the closest one says the village is one street you get around on foot with one car park — which is enough to answer the question, and generation did answer it correctly from that chunk. My retrieval rubric contradicts itself: it opens with "contains the expected fact, **or** contains the information needed to state it" and then ends with "the only question is whether the fact is present." The judge followed the stricter line and replied `NO` (logged in `results/judge_log_2026-09-29.jsonl`).<br><br>Under a consistent rubric this is probably 5 of 5. I kept 4 of 5 anyway: that number came from a rubric frozen before I read any results, and rewriting the rubric once I'd seen the outcome would make the count untrustworthy even though the edit would be a legitimate bug fix. The flawed rubric is recorded under What's Still Broken rather than patched mid-evaluation. Criterion 1 is MET either way, so nothing about this verdict depends on the choice. |
| 2 | Every answer names a source | MET | 5 of 5 in all three runs. For each of the 15 answers I checked whether it contained the filename of any chunk retrieved for it, accepting the name with or without `.md`. No model call: every chunk already carries its source, so this is an exact comparison against a known set rather than a judgment. |
| 3 | The relevance gate stops out-of-corpus questions | MET | 5 of 5 refused against a target of 4 of 5, from `run_eval.py::check_out_of_scope`. Not a close call — best distances ran 0.798 to 1.002 against a 0.6 cutoff, so the nearest one still had 0.198 of headroom. Measured in one deterministic pass, so the same number goes in all three run columns. |
| 4 | Chunks carry their document header | MISSED | 93 of 94. The header half passes outright: 94/94 chunks begin with their source filename. The length half fails on `guide_accessibility.md#1` at 784 characters against my 750 ceiling. My target said *every* chunk, so one failure is a miss — there is no "close" here, the target is absolute. Measured by `check_criterion_4.py`, saved to `results/criterion_4/`. |
| 5 | A user's time reference maps to the document's season or date range | MET | 2 of 2 in all three runs, decided by reading all six answers rather than spending model calls. Givens Mill gave both the season word and the range every time ("closed entirely in winter", "runs from March to November"); Brightwater gave the document's own range every time ("late September through November"). `scorer.py::states_time_reference` exists for this and I chose not to use it — the answers were unambiguous enough that reading them was the honest call, and it left the judge's cost for criterion 1 where it was actually needed. |

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

### Criterion 4 — stage: chunking

`guide_accessibility.md#1` came out at 784 characters, 34 over the 750
ceiling. Every other chunk fits, and all 94 carry their header, so the header
half of the criterion was never in question — this is a size failure alone.

The mechanism is in `chunker.py::split_documents`. My strategy is one chunk
per `##` section with no size cap, chosen because a section is usually one
complete thought and cutting inside it does more harm than good. That holds
for almost every section in the corpus. It doesn't hold for
`guide_accessibility.md`'s "Straightforward" section, which isn't one thought
— it's a list of three towns in three `**Town**` paragraphs, one after
another. A list has no natural length limit, so the strategy that protects a
single thought produces an oversized chunk when handed one.

Working backwards the way the brief suggests: the chunk exists, is
well-formed, and starts with its header, so loading is fine. The problem is
visible in the chunker's own output before anything is embedded, so it's not
retrieval and not generation. Chunking.

There is a second half to this that isn't the pipeline's fault. I set the
750 ceiling in week 1 by measuring 84 `##` sections at 177–712 characters and
adding ~40 for the header. The chunker actually produces 94 chunks reaching
784. I sampled the sections, not the chunks, and the sample missed the
largest one — so the bound was slightly too tight the day I wrote it. The
criterion was still correct and still measurable; I just couldn't have known
from my own notes that one section would break it.

### No pattern — one miss

With a single miss there is nothing to generalise from. Two observations
instead, both of which matter more than the miss did.

**Criterion 1 passed at exactly 4 of 5, with no margin.** A target hit exactly
is one bad retrieval away from failing, and it would be dishonest to read that
as comfortable. It is the criterion I would tighten if I were setting these
again — "the top three results contain the answer" rather than any of the top
five, which is a stricter claim about ranking and not just presence.

**One of my five numbers was wrong, and not because of any pipeline stage.**
`scorer.py::retrieval_hits` scored "Does Elder Ness have public transport?" as
a retrieval miss. The retrieved chunks describe a one-street village crossed
on foot with a single car park, which is enough to state that there is no
public transport, and `python app.py ask` produced exactly that answer from
those same chunks. My `RETRIEVAL_RUBRIC` contradicted itself — it opened by
allowing a fact that could be inferred and closed by requiring the fact to be
present — and the judge followed the stricter line.

That failure sits outside the five stages entirely. Loading, chunking,
embedding, retrieval and generation all did their job; the thing that got it
wrong was the instrument I built to measure them. It is the most useful thing
this test found, because a measurement error doesn't announce itself the way a
bad answer does — it just produces a confident number. I only caught it by
reading the chunks behind a verdict instead of trusting the verdict.

## The Improvement

**What I changed:** Chunking. `chunker.py::split_documents` made one chunk per
`##` section with no size cap, so a long section became a long chunk. It now
checks each section against the 150–750 bound and, when one is over, splits it
at paragraph breaks and re-prefixes the header onto every piece
(`chunker.py::_fit`). Sentence-level and hard cuts sit behind that as
fallbacks, so the bound holds whatever the corpus contains.

**Why I picked it:** Criterion 4 was my only miss, and the diagnosis named
chunking — `guide_accessibility.md#1` was 784 characters because its
"Straightforward" section describes three towns in three paragraphs, and my
chunker had no rule that could cut it.

Indexed as variant `v2` rather than rebuilt in place, so the old chunking is
still queryable for comparison: `python app.py --variant v2 index`.

### Run Log — After

`python run_eval.py --label after --variant v2` →
`results/run_2026-09-29_2012_after.md`, plus
`results/criterion_1/run{1,2,3}_after.txt` and
`results/criterion_4/run{1,2,3}_after.txt`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunks contain the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. The relevance gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks carry their document header | 95 of 95 | 95/95 | 95/95 | 95/95 | MET |
| 5. A user's time reference maps to the document's season or date range | 2 of 2 | 2/2 | 2/2 | 2/2 | MET |

Criterion 4's denominator moves from 94 to 95 because the fix splits one chunk
into two. The target itself is unchanged — it was always "every chunk", and
"every chunk" is now 95 of them.

| | Before | After |
|---|---|---|
| 1. Retrieved chunks contain the answer | 4/5 MET | 5/5 MET |
| 2. Every answer names a source | 5/5 MET | 5/5 MET |
| 3. Gate stops out-of-corpus questions | 5/5 MET | 5/5 MET |
| 4. Chunks carry their document header | 93/94 **MISSED** | 95/95 **MET** |
| 5. Time reference → season or date range | 2/2 MET | 2/2 MET |
| chunk size range | 196–784 | 196–680 |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

Yes, for the criterion it was aimed at. Criterion 4 went from MISSED to MET:
the longest chunk dropped from 784 characters to 680, all 95 chunks now sit
inside the 150–750 bound, and all 95 still carry their header.

Nothing regressed. Criteria 2, 3 and 5 are unchanged, and for four of the five
questions the best retrieval distance is identical before and after (0.373,
0.306, 0.349, 0.314) — only one chunk in the whole corpus was split, so most
questions never touched the change.

**Criterion 1's 4 of 5 → 5 of 5 is not from this change, and I want to be
clear about that.** Two things changed in this window: the chunking fix above,
and a separate fix to `RETRIEVAL_RUBRIC` in `scorer.py`, which had been
self-contradictory. I measured the rubric fix on its own against the *old*
index first, and it gave 5 of 5 by itself. So criterion 1 is the judge getting
a question right that it had been getting wrong, not retrieval improving. The
chunking change held it at 5 of 5 rather than causing it.

The honest cost of that: the milestone asks for one change, and there were two
in this window. The only reason I can attribute them separately is that they
were measured separately. Had I made both and run the test once, criterion 1's
gain would have been unattributable and I would have had no way to tell which
change earned it.

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

All five criteria are MET after the fix, so nothing is still missed. What is
still weak is how thinly most of them were tested — five questions is a small
number to conclude anything from, and four of the five below come down to
that.

**1. Retrieved chunks contain the answer — tested too narrowly.** Five
questions, and I wrote all five myself knowing what my corpus contained. That
biases them toward things I already knew were in there. A wider set, including
questions written without looking at the documents first, would tell me
something my current set can't. Ran out of time.

**2. Every answer names a source — solid, but it checks the weaker claim.**
The grounding instruction asks the model to name the file it used, and it does,
in all 15 answers across both runs. The check only verifies that the answer
names *one of* the five retrieved sources, though, not that it names the one
the answer actually came from. With `top_k=5` an answer could cite a file it
didn't use and still pass. Checking the stronger claim needs a way to tie a
sentence back to the chunk that produced it, which I don't have.

**3. The gate stops out-of-corpus questions — never tested near the boundary.**
It refused 5 of 5, but the closest out-of-scope question sat at 0.798 against a
0.6 cutoff. Nothing I asked landed anywhere near the line. That makes the
result a test of obviously-unrelated questions, not a test of the gate. What
would actually probe it is questions about the region that the guides happen
not to cover — a town not in the corpus, or a topic like train timetables —
which should land in the 0.5–0.7 band where the cutoff has to make a real
decision. Ran out of time.

**4. Chunks carry their document header — works here, breaks on a document
shaped differently.** Every chunk in `city_guides` carries its header because
every file starts with a `# Title` line. `chunker.py::split_documents` takes
line 1 as the title and doesn't check that it is one, so a new guide added in a
different shape degrades silently:

- A file starting with prose instead of `# Title` puts that first sentence
  into the header — and the intro block then drops line 1 as if it were a
  title, so the sentence is lost from the chunk body entirely. Verified: a
  document beginning "A headland village of 300." loses the population from
  its text and keeps it only in a malformed header.
- A file starting directly with `## Getting around` gives *every* chunk in
  that file the header "— Getting around", so the town name is wrong
  throughout.

Neither raises an error, and criterion 4's check wouldn't catch either: both
still "begin with the source filename". The fix is to detect a missing title
and fall back to the filename, plus a check that the title isn't a `##`
heading. I found this while writing up rather than while testing, so it is
diagnosed but not fixed.

**5. Time reference maps to season or date range — two questions is not
enough.** Both passed all three runs, but they cover one direction each:
December → "winter", October → "late September through November". The corpus
expresses time both as season words and as month ranges, and I tested one
example of each. A month that falls on a boundary — March for the Givens Mill
mill, which the guide says runs "March to November" — is where I'd expect this
to be shaky, and I didn't ask it.

**The judge itself.** `RETRIEVAL_RUBRIC` was self-contradictory and I only
caught it by reading the chunks behind one verdict. The systematic version of
that check — labelling a sample by hand and measuring how often the judge
agrees — is the thing that would have caught it in minutes rather than by
luck. I didn't run it.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

**Criterion 1, tightened.** It passed at exactly 4 of 5 before the rubric fix
— no margin at all. As written it asks only that the answer appear somewhere
in the top five, which says nothing about ranking. I'd write it as *the top
three results contain the answer*, which is a claim about retrieval putting
the right thing near the top rather than merely somewhere in the pile.

**Criterion 4, split in two.** It bundles two independent properties — every
chunk carries a header, and every chunk fits 150–750 characters. When it
failed, the single MISSED hid that the header half passed 94/94 and only the
size half broke. Two criteria would have said which.

**Criterion 4's bound, measured from the right thing.** I set 150–750 by
measuring 84 `##` sections at 177–712 characters and adding ~40 for the
header. But the chunker doesn't emit sections, it emits chunks, and there were
94 of them reaching 784. I measured the input to the thing I was bounding
instead of its output. Measuring the chunker's own output would have shown the
784 immediately — `chunker.py::describe` prints it, and `python app.py index`
had been printing it on every rebuild the whole time.

**Criterion 3, aimed at the boundary.** "Four of five out-of-corpus questions
refused" is satisfied by five questions that are nowhere near the cutoff, which
is what happened. I'd write it against questions that sit close to the line,
because that is the only place the threshold is doing work.

**And I'd build the judge's calibration step first.** I wrote an LLM judge and
trusted its numbers, and one of them was wrong. Labelling a handful of answers
by hand and checking the judge against them costs very little and is the only
thing that tells you whether the numbers mean anything. I treated it as
optional and it should have come before the first run.
