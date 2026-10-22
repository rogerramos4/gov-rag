"""Judge rubrics, kept in the repo so the write-up can quote exactly what was scored.

Why one rubric per failure mode: a single 1-5 "quality" score hides WHICH thing went
wrong. Binary Pass/Fail per mode is what 2026 eval practice recommends.
"""

CORRECTNESS = """You are grading an answer produced by a question-answering system.
You will see the QUESTION, a REFERENCE ANSWER written by a human, and the SYSTEM ANSWER.

PASS if the SYSTEM ANSWER conveys the same essential facts as the REFERENCE ANSWER.
Extra correct detail is fine. Different wording is fine. Omitting a minor detail is fine.
FAIL if the SYSTEM ANSWER contradicts the reference, misses the main point, or is an
abstention ("NOT IN DOCUMENTS") when the reference contains a real answer.

Ignore citations and formatting entirely; only judge factual content.
Reply with exactly one line: PASS or FAIL, then a hyphen, then one sentence of reason."""

GROUNDEDNESS = """You are checking whether an answer is supported by its source passages.
You will see the PASSAGES that were given to the system and the SYSTEM ANSWER.

PASS if every factual claim in the SYSTEM ANSWER can be traced to the PASSAGES.
Paraphrase is fine. An abstention ("NOT IN DOCUMENTS") always PASSES this check.
FAIL if the SYSTEM ANSWER states anything the PASSAGES do not say, including plausible
details that may be true in the real world but are not in the passages.

Ignore whether the answer is correct or complete; only judge support.
Reply with exactly one line: PASS or FAIL, then a hyphen, then one sentence of reason."""
