"""
Week 2: deciding whether an answer was right.

An LLM-as-judge scorer. This is how production RAG evaluation is actually
done — RAGAS, DeepEval, promptfoo, Braintrust and LangSmith all ship an LLM
judge — and the reason is that string matching cannot see paraphrase or
negation. Measured on this corpus's own phrasing:

  "no public transport" vs an answer saying the OPPOSITE  -> fuzzy score 89.5
  "40,000"              vs "4,000 residents"              -> fuzzy score 83.3

There is no threshold that separates those from genuine paraphrases, so fuzzy
matching is structurally unfit for judging correctness here, not merely
badly tuned.

The practices this file follows, all of them standard:

  • Binary verdicts, never a 1-5 score. LLM Likert scores are poorly
    calibrated and unstable between runs; YES/NO against one falsifiable
    question is not.
  • One dimension per call. Never "is this answer good".
  • The standard stated BEFORE the answer, and a bare one-word verdict
    demanded last. Cuts position bias and keeps replies parseable.
  • Deterministic checks wherever the claim has a canonical form —
    `names_source` spends no model call, because it doesn't need one.
  • Every raw reply logged, so a surprising number can be traced to what the
    judge actually said.

Written by Claude (Opus 5) at my direction — see README, How I Used AI.
"""

import datetime as dt
import json
import re

import config
import gate
import generate

# ─── The rubrics ─────────────────────────────────────────────────────────────
# These define what "correct" means. Changing the wording changes the
# standard, so they are frozen before a run log is read — tuning a rubric
# until the numbers pass is the same failure as lowering a missed target.

JUDGE_SYSTEM = """You grade answers against a standard, for an evaluation of a \
document retrieval system.

You are strict and literal. Wording may differ from the standard; meaning may \
not.

Reply with exactly one word: YES or NO. No explanation, no punctuation, no \
other word."""


ANSWER_RUBRIC = """The standard: the answer states the expected fact. Different \
wording, spelling, or phrasing is fine, and extra correct detail is fine.

The standard is NOT met if the answer states the opposite of the expected \
fact, omits it, hedges without committing to it, or answers some other \
question instead.

The expected fact: {expects}
The question asked: {question}
The answer given: {answer}

Does the answer meet the standard? One word."""


RETRIEVAL_RUBRIC = """The standard: at least one excerpt below contains the \
expected fact, or contains the information needed to state it.

These excerpts are raw source material, not answers. They may be fragmentary, \
may discuss other topics, and may bury the fact mid-paragraph. None of that \
matters. The only question is whether the fact is present in at least one of \
them.

The expected fact: {expects}

The excerpts:

{chunks}

Is the expected fact present in at least one excerpt? One word."""


TIME_RUBRIC = """The standard: the question asks about a specific time, such as \
a month. The answer meets the standard if it states the season, month range, \
or date range that applies — for example "winter", "late September through \
November", or "closed from November until March".

Naming the month from the question does not count on its own. The answer has \
to give the period the source material uses.

The standard is NOT met if the answer only says yes or no, only says that \
something is open or closed, or gives no time period at all.

The question asked: {question}
The answer given: {answer}

Does the answer meet the standard? One word."""


# ─── Plumbing ────────────────────────────────────────────────────────────────

def _verdict(raw: str) -> bool | None:
    """
    Parse a judge reply into True / False / None.

    None means "couldn't tell", and it is NOT the same as False. Mapping an
    unparseable reply to False silently inflates the failure count and sends
    you off diagnosing a retrieval bug that was really a judge replying
    "Unclear". Callers decide what to do with None; the log always records it.

    Handles YES, Yes., **YES**, `yes`, "> YES", and "yes - because ..." alike.
    """
    if not raw:
        return None
    cleaned = raw.strip().lstrip("*_#`> \t\n")
    match = re.match(r"[A-Za-z]+", cleaned)
    if not match:
        return None
    word = match.group(0).upper()
    if word == "YES":
        return True
    if word == "NO":
        return False
    return None


def _ask(rubric: str, dimension: str, subject: str, **fields) -> bool | None:
    """
    One judgment, logged.

    cache=True on purpose. generate.py keys its cache on (model, system,
    prompt), so an identical answer judged against an identical rubric yields
    an identical verdict — which is what makes a run log reproducible, and
    makes re-running while drafting the README cost nothing.

    That is deliberately the opposite of run_eval.py's cache=False, for the
    opposite reason: three runs of the pipeline must be three real answers,
    but one answer must get one stable verdict.
    """
    if not rubric.strip() or not JUDGE_SYSTEM.strip():
        raise RuntimeError(
            f"The {dimension} rubric is empty — there is no standard to judge "
            f"against. Restore the rubric constants at the top of scorer.py."
        )

    raw = generate.generate(rubric.format(**fields), system=JUDGE_SYSTEM, cache=True)
    verdict = _verdict(raw)
    _log(dimension, subject, verdict, raw)
    return verdict


def _log(dimension: str, subject: str, verdict: bool | None, raw: str) -> None:
    """
    Append the judge's raw reply to results/.

    A verdict you can't inspect isn't evidence. When a number in the run log
    looks wrong, this file is how you tell a pipeline failure from a judge
    that misread its rubric. Accounting never breaks the thing it accounts
    for, so this swallows its own errors.
    """
    try:
        config.RESULTS_DIR.mkdir(exist_ok=True)
        path = config.RESULTS_DIR / f"judge_log_{dt.date.today():%Y-%m-%d}.jsonl"
        record = {
            "when": dt.datetime.now().isoformat(timespec="seconds"),
            "dimension": dimension,
            "subject": subject,
            "verdict": verdict,
            "raw": raw,
        }
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


def is_refusal(answer: str) -> bool:
    """
    Did the gate refuse before the model was ever called?

    run_eval.py passes gate.REFUSAL straight through as the answer when the
    best distance was over the cutoff. For an IN-SCOPE question that is a fail
    by definition, so there is no reason to spend a model call asking whether
    a refusal states a fact.

    (For OUT_OF_SCOPE questions a refusal is the *correct* outcome, but those
    never reach this file — run_eval.py::check_out_of_scope scores them
    separately, against criterion 3.)
    """
    return answer.strip() == gate.REFUSAL.strip()


# ─── The judgments ───────────────────────────────────────────────────────────

def judge(question, expects, answer, results) -> bool:
    """
    Did the answer state the expected fact? This is the verdict run_eval.py
    records in the Run columns.

    Returns bool because run_eval.py's table needs one. An unparseable judge
    reply therefore lands here as False — but _ask has already written it to
    the judge log with its raw text, so an inflated failure count can always
    be traced back to the reply that caused it.
    """
    if is_refusal(answer):
        _log("answer", question, False, "(gate refused — no model call made)")
        return False

    verdict = _ask(
        ANSWER_RUBRIC, "answer", question,
        expects=expects, question=question, answer=answer,
    )
    return verdict is True


def retrieval_hits(expects, results) -> bool:
    """
    Criterion 1: do the retrieved chunks contain the answer?

    Judged against the CHUNKS, never the generated answer. If retrieval were
    scored by reading the answer, a generation failure would be filed as a
    retrieval failure — and week 2 is graded on naming which stage broke.

    Costs one call per question rather than one per run: store.py::search is
    deterministic, so the same question retrieves the same chunks every run,
    which makes the judge prompt identical and runs 2 and 3 cache hits.
    """
    if not results:
        return False

    chunks = "\n\n".join(f"[{r.label}]\n{r.text}" for r in results)
    verdict = _ask(
        RETRIEVAL_RUBRIC, "retrieval", expects,
        expects=expects, chunks=chunks,
    )
    return verdict is True


def names_source(answer, results) -> bool:
    """
    Criterion 2: does the answer name at least one source document?

    Deterministic, and no model call — every Result already carries .source
    (store.py), so this is a string comparison against a known set of
    filenames rather than a language judgment. Spending a call here would buy
    nothing.

    Accepts the filename with or without its extension, since an answer may
    cite "guide_brightwater" rather than "guide_brightwater.md".
    """
    if is_refusal(answer) or not results:
        return False

    text = answer.lower()
    for result in results:
        source = result.source.lower()
        if source and source in text:
            return True
        stem = source.rsplit(".", 1)[0]
        if stem and stem in text:
            return True
    return False


def states_time_reference(question, answer) -> bool:
    """
    Criterion 5: does the answer map the user's month onto the season or date
    range the document uses?

    The one judgment in this file that no string method can make. "December"
    and "winter" share no characters; "October" and "late September through
    November" share none either. It is an inference about meaning, which is
    exactly where an LLM judge earns its cost.
    """
    if is_refusal(answer):
        _log("time", question, False, "(gate refused — no model call made)")
        return False

    verdict = _ask(TIME_RUBRIC, "time", question, question=question, answer=answer)
    return verdict is True
