# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in week 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next week costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
For city guides, the town name lives in the header, not in every paragraph, so a chunk cut by paragraph can lose its town reference. A question about a town whose fact sits in one of those paragraphs may retrieve the wrong town's chunk.
<!-- e.g. "One of my questions is about a topic only two documents mention, so
     I expect that one to be hard." -->

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
Each chunk stores its source file name as metadata, so the source is always available when an answer is generated. The only way this fails is if the response step doesn't carry that metadata into the answer.
<!-- Why all five and not four? What about your setup makes that achievable —
     or what would have to go wrong for it not to be? -->

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
The starter cutoff is 0.6, and config.py notes most corpora land between
0.45 and 0.75. I'll measure the best distance for my five in-scope and five
out-of-scope questions in Milestone 4 and expect a visible gap between the
two groups. The out-of-scope questions (diesel engines, ibuprofen, Rust) are
semantically far from a travel corpus, so I expect the gate to catch them.
I'm allowing one miss because "What is the capital of Mongolia?" is still a
place question and the closest of the five to city_guides.

<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->

---

## 4. Chunks carry their document header

Every chunk begins with its source file name and the document's main title
(e.g. "guide_walking.md — Walking in the region"), and every chunk is between
150 and 750 characters including that header.

**Why this target:**
In city_guides the town name lives in the document title, not in every
paragraph, so a chunk split at a subheader would otherwise lose its town.
Prepending the header fixes that. The size bound comes from measuring the
84 `##` sections: 177–712 characters, plus a ~40-character header. A chunk
outside 150–750 means the split didn't land on a subheader boundary.
---

## 5. A user's time reference maps to the document's season or date range

For both test questions that ask about a specific time (December for
Givens Mill, October for Brightwater), the answer states the season or date
range the document gives, whether the document uses a month range
("late September through November") or a season word ("winter") — 2 of 2.

**Why this target:**
The corpus expresses time as ranges or season words, while users ask by
month. The model has to map one to the other in both directions, and that
mapping is where I expect the answer to be wrong. With two questions
there's no reason to accept less than both.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     WEEK 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in week 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
